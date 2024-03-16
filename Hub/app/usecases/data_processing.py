from app.entities.agent_data import AgentData
from app.entities.processed_agent_data import ProcessedAgentData

def gen_state_by_z_axis(data:float):
    if(data<=5000):
        return "OK"
    if(data<=10000):
        return "Not that good"
    if(data<=15000):
        return "Poor"
    if(data<=20000):
        return "Extremely bad"
    return "What is it?"

def process_agent_data(
    agent_data: AgentData,
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    res = ProcessedAgentData(road_state=gen_state_by_z_axis(agent_data.accelerometer.z),agent_data=agent_data)
    return res
