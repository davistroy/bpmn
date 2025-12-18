# BPMN 2.0 Elements Reference

This document provides a quick reference for BPMN 2.0 elements supported by the bpmn-diagram skill.

## Events

Events represent something that happens during a process.

### Start Events

| Element | XML Tag | Description |
|---------|---------|-------------|
| None Start | `<startEvent>` | Generic process start |
| Message Start | `<startEvent><messageEventDefinition/></startEvent>` | Starts when message received |
| Timer Start | `<startEvent><timerEventDefinition/></startEvent>` | Starts at scheduled time |
| Signal Start | `<startEvent><signalEventDefinition/></startEvent>` | Starts on broadcast signal |
| Conditional Start | `<startEvent><conditionalEventDefinition/></startEvent>` | Starts when condition met |

### End Events

| Element | XML Tag | Description |
|---------|---------|-------------|
| None End | `<endEvent>` | Generic process end |
| Message End | `<endEvent><messageEventDefinition/></endEvent>` | Sends message on completion |
| Error End | `<endEvent><errorEventDefinition/></endEvent>` | Ends with error |
| Terminate End | `<endEvent><terminateEventDefinition/></endEvent>` | Terminates all activities |
| Signal End | `<endEvent><signalEventDefinition/></endEvent>` | Broadcasts signal on end |

### Intermediate Events

| Element | XML Tag | Description |
|---------|---------|-------------|
| Catch Message | `<intermediateCatchEvent><messageEventDefinition/></intermediateCatchEvent>` | Waits for message |
| Throw Message | `<intermediateThrowEvent><messageEventDefinition/></intermediateThrowEvent>` | Sends message |
| Timer | `<intermediateCatchEvent><timerEventDefinition/></intermediateCatchEvent>` | Waits for time |
| Signal Catch | `<intermediateCatchEvent><signalEventDefinition/></intermediateCatchEvent>` | Waits for signal |
| Signal Throw | `<intermediateThrowEvent><signalEventDefinition/></intermediateThrowEvent>` | Broadcasts signal |
| Link Catch | `<intermediateCatchEvent><linkEventDefinition/></intermediateCatchEvent>` | Off-page connector (target) |
| Link Throw | `<intermediateThrowEvent><linkEventDefinition/></intermediateThrowEvent>` | Off-page connector (source) |

### Boundary Events

Boundary events are attached to activities and trigger when specific conditions occur.

```xml
<boundaryEvent id="BoundaryEvent_1" attachedToRef="Task_1">
  <timerEventDefinition/>
</boundaryEvent>
```

## Activities

Activities represent work performed in a process.

### Tasks

| Element | XML Tag | Description |
|---------|---------|-------------|
| Task | `<task>` | Generic task |
| User Task | `<userTask>` | Performed by human |
| Service Task | `<serviceTask>` | Automated service call |
| Script Task | `<scriptTask>` | Executes a script |
| Send Task | `<sendTask>` | Sends a message |
| Receive Task | `<receiveTask>` | Waits for message |
| Manual Task | `<manualTask>` | Manual work outside system |
| Business Rule Task | `<businessRuleTask>` | Executes business rules |

### Sub-Processes

| Element | XML Tag | Description |
|---------|---------|-------------|
| Sub-Process | `<subProcess>` | Embedded sub-process |
| Call Activity | `<callActivity>` | Calls external process |
| Transaction | `<transaction>` | Transactional sub-process |
| Event Sub-Process | `<subProcess triggeredByEvent="true">` | Event-triggered sub-process |

### Multi-Instance

Activities can be marked as multi-instance (loop):

```xml
<task id="Task_1">
  <multiInstanceLoopCharacteristics isSequential="false"/>
</task>
```

## Gateways

Gateways control flow divergence and convergence.

| Element | XML Tag | Symbol | Description |
|---------|---------|--------|-------------|
| Exclusive (XOR) | `<exclusiveGateway>` | X | One path based on condition |
| Parallel (AND) | `<parallelGateway>` | + | All paths simultaneously |
| Inclusive (OR) | `<inclusiveGateway>` | O | One or more paths |
| Event-Based | `<eventBasedGateway>` | Pentagon | Path based on event |
| Complex | `<complexGateway>` | * | Complex conditions |

### Gateway Example

```xml
<exclusiveGateway id="Gateway_1" name="Decision">
  <incoming>Flow_1</incoming>
  <outgoing>Flow_2</outgoing>
  <outgoing>Flow_3</outgoing>
</exclusiveGateway>

<sequenceFlow id="Flow_2" sourceRef="Gateway_1" targetRef="Task_A">
  <conditionExpression>${approved == true}</conditionExpression>
</sequenceFlow>

<sequenceFlow id="Flow_3" sourceRef="Gateway_1" targetRef="Task_B">
  <conditionExpression>${approved == false}</conditionExpression>
</sequenceFlow>
```

## Flows

Flows connect elements in a process.

| Element | XML Tag | Description |
|---------|---------|-------------|
| Sequence Flow | `<sequenceFlow>` | Order of activities |
| Message Flow | `<messageFlow>` | Message between participants |
| Association | `<association>` | Links artifacts to elements |
| Data Association | `<dataInputAssociation>` / `<dataOutputAssociation>` | Data flow |

### Sequence Flow with Condition

```xml
<sequenceFlow id="Flow_1" sourceRef="Gateway_1" targetRef="Task_1">
  <conditionExpression xsi:type="tFormalExpression">
    ${amount > 1000}
  </conditionExpression>
</sequenceFlow>
```

## Swimlanes

Swimlanes organize process participants.

### Pools (Participants)

```xml
<collaboration id="Collaboration_1">
  <participant id="Participant_1" name="Customer" processRef="Process_Customer"/>
  <participant id="Participant_2" name="Supplier" processRef="Process_Supplier"/>
  <messageFlow id="MsgFlow_1" sourceRef="Task_Order" targetRef="Task_Receive"/>
</collaboration>
```

### Lanes

```xml
<process id="Process_1">
  <laneSet id="LaneSet_1">
    <lane id="Lane_Manager" name="Manager">
      <flowNodeRef>Task_Approve</flowNodeRef>
    </lane>
    <lane id="Lane_Employee" name="Employee">
      <flowNodeRef>Task_Submit</flowNodeRef>
    </lane>
  </laneSet>
</process>
```

## Data

Data elements represent information in a process.

| Element | XML Tag | Description |
|---------|---------|-------------|
| Data Object | `<dataObjectReference>` | Data within process |
| Data Store | `<dataStoreReference>` | Persistent data storage |
| Data Input | `<dataInput>` | Process input data |
| Data Output | `<dataOutput>` | Process output data |

## Artifacts

Artifacts provide additional information.

| Element | XML Tag | Description |
|---------|---------|-------------|
| Text Annotation | `<textAnnotation>` | Comments and notes |
| Group | `<group>` | Visual grouping |

### Text Annotation Example

```xml
<textAnnotation id="TextAnnotation_1">
  <text>This task requires manager approval</text>
</textAnnotation>
<association id="Association_1" sourceRef="Task_1" targetRef="TextAnnotation_1"/>
```

## Diagram Interchange (DI)

The DI section defines visual layout. Required for rendering.

```xml
<bpmndi:BPMNDiagram id="BPMNDiagram_1">
  <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">

    <!-- Shape for a task -->
    <bpmndi:BPMNShape id="Task_1_di" bpmnElement="Task_1">
      <dc:Bounds x="200" y="100" width="100" height="80"/>
    </bpmndi:BPMNShape>

    <!-- Shape for a gateway -->
    <bpmndi:BPMNShape id="Gateway_1_di" bpmnElement="Gateway_1" isMarkerVisible="true">
      <dc:Bounds x="350" y="115" width="50" height="50"/>
    </bpmndi:BPMNShape>

    <!-- Edge for a sequence flow -->
    <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
      <di:waypoint x="300" y="140"/>
      <di:waypoint x="350" y="140"/>
    </bpmndi:BPMNEdge>

  </bpmndi:BPMNPlane>
</bpmndi:BPMNDiagram>
```

## Namespaces

Standard BPMN 2.0 namespaces:

```xml
xmlns="http://www.omg.org/spec/BPMN/20100524/MODEL"
xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
```

## Resources

- [BPMN 2.0 Specification (OMG)](https://www.omg.org/spec/BPMN/2.0/)
- [bpmn.io Documentation](https://bpmn.io/)
- [BPMN Quick Guide](https://www.bpmn.org/)
