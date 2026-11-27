from state import TaskState

state = TaskState("check_state")

state.record(
    "product_info",
    '{"product": "рис"}',
    "Калорійність: 344 ккал на 100 г"
)

print(state.render())