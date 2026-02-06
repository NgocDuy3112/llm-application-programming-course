from tests import test_chat_service as m

# inspect sliding_window_basic
history = m.make_history(20)
out = m.ChatService.sliding_window(history, 5)
print('out length:', len(out))
print('out repr:', out)
print('expected:', history[-5:])

# inspect create_response_respects_sliding_window
client = m.DummyClient()
svc = m.ChatService(client)
history = m.make_history(30)
svc.create_response(
    mode='non-streaming',
    input_data=history,
    use_sliding_window=True,
    max_history_messages=7,
)
print('client.last_kwargs input length:', len(client.last_kwargs['input']))
print('client.last_kwargs input:', client.last_kwargs['input'])
