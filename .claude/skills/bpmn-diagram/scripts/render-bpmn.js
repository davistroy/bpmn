#!/usr/bin/env node

/**
 * BPMN to PNG Renderer
 *
 * Converts BPMN 2.0 XML files to PNG images using bpmn-js with jsdom/canvas.
 * No browser required - pure Node.js rendering.
 *
 * Usage:
 *   node render-bpmn.js <input.bpmn> <output.png> [options]
 *
 * Options:
 *   --scale=N              Image scale factor (default: 1)
 *   --min-dimensions=WxH   Minimum dimensions in pixels (default: 800x600)
 *   --padding=N            Padding around diagram in pixels (default: 20)
 *
 * Examples:
 *   node render-bpmn.js diagram.bpmn diagram.png
 *   node render-bpmn.js diagram.bpmn diagram.png --scale=2
 */

const fs = require('fs');
const path = require('path');
const { JSDOM } = require('jsdom');
const { createCanvas, loadImage } = require('canvas');

// Parse command line arguments
function parseArgs(args) {
    const options = {
        input: null,
        output: null,
        scale: 1,
        minDimensions: { width: 800, height: 600 },
        padding: 20
    };

    for (const arg of args) {
        if (arg.startsWith('--scale=')) {
            options.scale = parseFloat(arg.split('=')[1]) || 1;
        } else if (arg.startsWith('--min-dimensions=')) {
            const dims = arg.split('=')[1];
            const [width, height] = dims.split('x').map(Number);
            if (width && height) {
                options.minDimensions = { width, height };
            }
        } else if (arg.startsWith('--padding=')) {
            options.padding = parseInt(arg.split('=')[1], 10) || 20;
        } else if (!arg.startsWith('--')) {
            if (!options.input) {
                options.input = arg;
            } else if (!options.output) {
                options.output = arg;
            }
        }
    }

    return options;
}

// Validate BPMN XML content
function validateBpmn(content, filePath) {
    if (!content.includes('<?xml') && !content.includes('<definitions')) {
        throw new Error(`File "${filePath}" does not appear to be valid XML`);
    }

    if (!content.includes('<definitions') && !content.includes('<bpmn:definitions')) {
        throw new Error(
            `File "${filePath}" is not valid BPMN 2.0 format. ` +
            `Missing <definitions> root element with BPMN namespace.`
        );
    }

    const hasBpmnNamespace =
        content.includes('http://www.omg.org/spec/BPMN/20100524/MODEL') ||
        content.includes('xmlns:bpmn=') ||
        content.includes('xmlns="http://www.omg.org/spec/BPMN');

    if (!hasBpmnNamespace) {
        console.warn(
            `Warning: File "${filePath}" may not have proper BPMN 2.0 namespace.`
        );
    }

    const hasDiagram =
        content.includes('<bpmndi:BPMNDiagram') ||
        content.includes('<BPMNDiagram') ||
        content.includes('BPMNDiagram');

    if (!hasDiagram) {
        console.warn(
            `Warning: File "${filePath}" has no diagram interchange (BPMNDiagram). ` +
            `The diagram may not render with proper layout.`
        );
    }

    return true;
}

// Setup jsdom environment for bpmn-js with SVG polyfills
function setupDom() {
    const html = `<!DOCTYPE html>
<html>
<head>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        #canvas { width: 2000px; height: 2000px; }
    </style>
</head>
<body>
    <div id="canvas"></div>
</body>
</html>`;

    const dom = new JSDOM(html, {
        pretendToBeVisual: true,
        runScripts: 'dangerously',
        resources: 'usable'
    });

    const { window } = dom;

    // Polyfill getBBox for SVG elements
    const originalCreateElementNS = window.document.createElementNS.bind(window.document);
    window.document.createElementNS = function(namespaceURI, qualifiedName) {
        const element = originalCreateElementNS(namespaceURI, qualifiedName);

        // Add getBBox polyfill for SVG elements
        if (namespaceURI === 'http://www.w3.org/2000/svg') {
            if (!element.getBBox) {
                element.getBBox = function() {
                    // Try to calculate bounds from attributes
                    const x = parseFloat(this.getAttribute('x')) || 0;
                    const y = parseFloat(this.getAttribute('y')) || 0;
                    const width = parseFloat(this.getAttribute('width')) || 100;
                    const height = parseFloat(this.getAttribute('height')) || 100;

                    // For path elements, try to get bounds from d attribute
                    if (this.tagName === 'path') {
                        const d = this.getAttribute('d');
                        if (d) {
                            const bounds = getPathBounds(d);
                            return bounds;
                        }
                    }

                    // For g elements, calculate from children
                    if (this.tagName === 'g') {
                        let minX = Infinity, minY = Infinity;
                        let maxX = -Infinity, maxY = -Infinity;

                        const children = this.querySelectorAll('*');
                        children.forEach(child => {
                            if (child.getBBox) {
                                try {
                                    const childBox = child.getBBox();
                                    minX = Math.min(minX, childBox.x);
                                    minY = Math.min(minY, childBox.y);
                                    maxX = Math.max(maxX, childBox.x + childBox.width);
                                    maxY = Math.max(maxY, childBox.y + childBox.height);
                                } catch (e) {}
                            }
                        });

                        if (minX !== Infinity) {
                            return {
                                x: minX, y: minY,
                                width: maxX - minX,
                                height: maxY - minY
                            };
                        }
                    }

                    return { x, y, width, height };
                };
            }

            if (!element.getBoundingClientRect) {
                element.getBoundingClientRect = function() {
                    const bbox = this.getBBox();
                    return {
                        x: bbox.x, y: bbox.y,
                        width: bbox.width, height: bbox.height,
                        top: bbox.y, left: bbox.x,
                        right: bbox.x + bbox.width,
                        bottom: bbox.y + bbox.height
                    };
                };
            }

            if (!element.getScreenCTM) {
                element.getScreenCTM = function() {
                    return {
                        a: 1, b: 0, c: 0, d: 1, e: 0, f: 0,
                        inverse: () => ({ a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 })
                    };
                };
            }

            if (!element.getCTM) {
                element.getCTM = function() {
                    return { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 };
                };
            }

            if (!element.createSVGPoint) {
                element.createSVGPoint = function() {
                    return { x: 0, y: 0, matrixTransform: () => ({ x: 0, y: 0 }) };
                };
            }

            // Add transform property polyfill
            if (!element.transform) {
                Object.defineProperty(element, 'transform', {
                    get: function() {
                        return {
                            baseVal: {
                                numberOfItems: 0,
                                getItem: () => ({
                                    matrix: { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 },
                                    setTranslate: () => {}
                                }),
                                consolidate: () => ({
                                    matrix: { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 }
                                }),
                                appendItem: (item) => item,
                                clear: () => {}
                            }
                        };
                    }
                });
            }

            // Add ownerSVGElement and createSVGTransform
            if (qualifiedName === 'svg') {
                if (!element.createSVGTransform) {
                    element.createSVGTransform = function() {
                        return {
                            matrix: { a: 1, b: 0, c: 0, d: 1, e: 0, f: 0 },
                            setTranslate: function(tx, ty) {
                                this.matrix.e = tx;
                                this.matrix.f = ty;
                            },
                            setMatrix: function(m) {
                                this.matrix = { ...m };
                            },
                            setRotate: function() {},
                            setScale: function() {},
                            setSkewX: function() {},
                            setSkewY: function() {}
                        };
                    };
                }

                if (!element.createSVGPoint) {
                    element.createSVGPoint = function() {
                        return {
                            x: 0,
                            y: 0,
                            matrixTransform: function(matrix) {
                                return {
                                    x: matrix.a * this.x + matrix.c * this.y + matrix.e,
                                    y: matrix.b * this.x + matrix.d * this.y + matrix.f
                                };
                            }
                        };
                    };
                }

                if (!element.createSVGMatrix) {
                    element.createSVGMatrix = function() {
                        return {
                            a: 1, b: 0, c: 0, d: 1, e: 0, f: 0,
                            multiply: function(m) { return this; },
                            inverse: function() { return this; },
                            translate: function(x, y) {
                                return { ...this, e: this.e + x, f: this.f + y };
                            },
                            scale: function(s) { return this; },
                            rotate: function(a) { return this; }
                        };
                    };
                }
            }

            // Point to ownerSVGElement
            if (!element.ownerSVGElement && qualifiedName !== 'svg') {
                Object.defineProperty(element, 'ownerSVGElement', {
                    get: function() {
                        let parent = this.parentNode;
                        while (parent) {
                            if (parent.tagName === 'svg') return parent;
                            parent = parent.parentNode;
                        }
                        return null;
                    }
                });
            }
        }

        return element;
    };

    // Helper function to get path bounds
    function getPathBounds(d) {
        const numbers = d.match(/-?\d+(\.\d+)?/g) || [];
        if (numbers.length < 2) {
            return { x: 0, y: 0, width: 100, height: 100 };
        }

        let minX = Infinity, minY = Infinity;
        let maxX = -Infinity, maxY = -Infinity;

        for (let i = 0; i < numbers.length - 1; i += 2) {
            const x = parseFloat(numbers[i]);
            const y = parseFloat(numbers[i + 1]);
            if (!isNaN(x) && !isNaN(y)) {
                minX = Math.min(minX, x);
                minY = Math.min(minY, y);
                maxX = Math.max(maxX, x);
                maxY = Math.max(maxY, y);
            }
        }

        if (minX === Infinity) {
            return { x: 0, y: 0, width: 100, height: 100 };
        }

        return {
            x: minX, y: minY,
            width: maxX - minX || 100,
            height: maxY - minY || 100
        };
    }

    // SVG Matrix class polyfill
    class SVGMatrixPolyfill {
        constructor(a = 1, b = 0, c = 0, d = 1, e = 0, f = 0) {
            this.a = a; this.b = b; this.c = c;
            this.d = d; this.e = e; this.f = f;
        }
        multiply(m) {
            return new SVGMatrixPolyfill(
                this.a * m.a + this.c * m.b,
                this.b * m.a + this.d * m.b,
                this.a * m.c + this.c * m.d,
                this.b * m.c + this.d * m.d,
                this.a * m.e + this.c * m.f + this.e,
                this.b * m.e + this.d * m.f + this.f
            );
        }
        inverse() { return new SVGMatrixPolyfill(); }
        translate(x, y) {
            return new SVGMatrixPolyfill(this.a, this.b, this.c, this.d, this.e + x, this.f + y);
        }
        scale(s) { return new SVGMatrixPolyfill(this.a * s, this.b, this.c, this.d * s, this.e, this.f); }
        rotate(angle) { return this; }
    }

    // Set up global browser environment
    global.SVGMatrix = SVGMatrixPolyfill;
    global.window = window;
    window.SVGMatrix = SVGMatrixPolyfill;
    global.document = window.document;
    global.navigator = window.navigator;
    global.DOMParser = window.DOMParser;
    global.Element = window.Element;
    global.HTMLElement = window.HTMLElement;
    global.SVGElement = window.SVGElement;
    global.Node = window.Node;
    global.NodeList = window.NodeList;
    global.Text = window.Text;
    global.DocumentFragment = window.DocumentFragment;
    global.getComputedStyle = window.getComputedStyle;
    global.requestAnimationFrame = (cb) => setTimeout(cb, 16);
    global.cancelAnimationFrame = (id) => clearTimeout(id);
    global.ResizeObserver = class ResizeObserver {
        observe() {}
        unobserve() {}
        disconnect() {}
    };

    return dom;
}

// Convert SVG string to PNG buffer
async function svgToPng(svgString, width, height, scale = 1) {
    const canvas = createCanvas(width * scale, height * scale);
    const ctx = canvas.getContext('2d');

    // Set white background
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Scale for higher resolution
    ctx.scale(scale, scale);

    // Create data URL from SVG
    const svgBase64 = Buffer.from(svgString).toString('base64');
    const dataUrl = `data:image/svg+xml;base64,${svgBase64}`;

    // Load and draw SVG
    const img = await loadImage(dataUrl);
    ctx.drawImage(img, 0, 0, width, height);

    return canvas.toBuffer('image/png');
}

// Main render function
async function renderBpmn(options) {
    const { input, output, scale, minDimensions, padding } = options;

    // Validate input file exists
    if (!fs.existsSync(input)) {
        throw new Error(`Input file not found: ${input}`);
    }

    // Read and validate BPMN content
    const bpmnXml = fs.readFileSync(input, 'utf-8');
    validateBpmn(bpmnXml, input);

    // Ensure output directory exists
    const outputDir = path.dirname(output);
    if (outputDir && outputDir !== '.' && !fs.existsSync(outputDir)) {
        fs.mkdirSync(outputDir, { recursive: true });
    }

    // Setup DOM environment BEFORE requiring bpmn-js
    setupDom();

    console.log(`Rendering BPMN diagram...`);
    console.log(`  Input:  ${path.resolve(input)}`);
    console.log(`  Output: ${path.resolve(output)}`);
    console.log(`  Scale:  ${scale}`);

    try {
        // Load the bundled bpmn-js viewer (UMD build)
        const BpmnViewer = require('./node_modules/bpmn-js/dist/bpmn-viewer.development.js');

        // Create container
        const container = document.getElementById('canvas');

        // Create viewer instance
        const viewer = new BpmnViewer({
            container: container
        });

        // Import BPMN XML
        await viewer.importXML(bpmnXml);

        // Get the SVG
        const { svg } = await viewer.saveSVG();

        // Parse SVG to get dimensions from viewBox
        const viewBoxMatch = svg.match(/viewBox="([^"]+)"/);
        let width = minDimensions.width;
        let height = minDimensions.height;

        if (viewBoxMatch) {
            const parts = viewBoxMatch[1].split(/\s+/).map(Number);
            if (parts.length >= 4) {
                const [, , vbWidth, vbHeight] = parts;
                width = Math.max(Math.ceil(vbWidth) + padding * 2, minDimensions.width);
                height = Math.max(Math.ceil(vbHeight) + padding * 2, minDimensions.height);
            }
        }

        // Update SVG with proper dimensions
        let finalSvg = svg;

        // Replace or add width/height attributes
        if (finalSvg.match(/width="[^"]*"/)) {
            finalSvg = finalSvg.replace(/width="[^"]*"/, `width="${width}"`);
        } else {
            finalSvg = finalSvg.replace('<svg', `<svg width="${width}"`);
        }

        if (finalSvg.match(/height="[^"]*"/)) {
            finalSvg = finalSvg.replace(/height="[^"]*"/, `height="${height}"`);
        } else {
            finalSvg = finalSvg.replace('<svg', `<svg height="${height}"`);
        }

        // Convert SVG to PNG
        const pngBuffer = await svgToPng(finalSvg, width, height, scale);

        // Write output file
        fs.writeFileSync(output, pngBuffer);

        // Verify output was created
        const stats = fs.statSync(output);
        console.log(`\nSuccess! Created ${output} (${formatBytes(stats.size)})`);
        console.log(`  Dimensions: ${Math.round(width * scale)}x${Math.round(height * scale)}px`);

        // Cleanup
        viewer.destroy();

        return { success: true, output: path.resolve(output), size: stats.size };
    } catch (err) {
        throw new Error(`Failed to render diagram: ${err.message}`);
    }
}

// Format bytes to human readable
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Print usage information
function printUsage() {
    console.log(`
BPMN to PNG Renderer

Usage:
  node render-bpmn.js <input.bpmn> <output.png> [options]

Arguments:
  input.bpmn    Path to BPMN 2.0 XML file
  output.png    Path for output PNG image

Options:
  --scale=N              Image scale factor (default: 1)
  --min-dimensions=WxH   Minimum dimensions in pixels (default: 800x600)
  --padding=N            Padding around diagram in pixels (default: 20)
  --help                 Show this help message

Examples:
  node render-bpmn.js diagram.bpmn diagram.png
  node render-bpmn.js diagram.bpmn diagram.png --scale=2
  node render-bpmn.js process.bpmn output.png --min-dimensions=1200x800
`);
}

// CLI entry point
async function main() {
    const args = process.argv.slice(2);

    if (args.includes('--help') || args.includes('-h') || args.length === 0) {
        printUsage();
        process.exit(0);
    }

    const options = parseArgs(args);

    if (!options.input) {
        console.error('Error: No input file specified');
        printUsage();
        process.exit(1);
    }

    if (!options.output) {
        console.error('Error: No output file specified');
        printUsage();
        process.exit(1);
    }

    try {
        await renderBpmn(options);
        process.exit(0);
    } catch (err) {
        console.error(`\nError: ${err.message}`);
        process.exit(1);
    }
}

if (require.main === module) {
    main();
}

module.exports = { renderBpmn, validateBpmn, parseArgs };
