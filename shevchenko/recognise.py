
def recognise(speak_model, model, tokenizer, lbl_encoder):
    while True:
        text = listen()
        print(text)

        trg = data_set.triggers.intersection(text.split())
        if not trg:
            continue

        text.replace(list(trg)[0], '')

        with open("../voice_assistant_data/intents.json", encoding='utf-8') as file:
            data = json.load(file)

        max_len = 20
        result = model.predict(keras.preprocessing.sequence.pad_sequences(tokenizer.texts_to_sequences([text]),
                                                                          truncating='post', maxlen=max_len))

        # вероятность распознавания - то, что фраза реально подходит под pattern
        max_arg = np.argmax(result)

        # Получение tag
        tag = lbl_encoder.inverse_transform([max_arg])

        # Получение вероятности предсказания для наиболее вероятного класса
        predicted_probability = result[0][max_arg]
        print(predicted_probability)

        # Определение порогового значения
        threshold = 0.902

        # Если вероятность предсказания выше порогового значения, считаем его достоверным
        if predicted_probability > threshold:
            for i in data['intents']:
                if i['tag'] == tag:
                    parts = i['tag'].split(' ')
                    state = parts[0]
                    function = parts[1]
                    if state == 'active':
                        say(random.choice(i['responses']), speak_model)
                        exec(function + '(speak_model)')
                    else:
                        say(random.choice(i['responses']), speak_model)
        else:
            say("К сожалению, я пока не знаю, что вам ответить", speak_model)
