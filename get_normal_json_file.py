import json

with open('file.json', encoding='utf-8') as file:
    data = json.load(file)


signs = ".-?![]"

for element in data['intents']:
    for i in range(0, len(element['patterns'])):
        element['patterns'][i] = element['patterns'][i].lower()
        element['patterns'][i] = element['patterns'][i].replace('.', '')
        element['patterns'][i] = element['patterns'][i].replace('?', '')
        element['patterns'][i] = element['patterns'][i].replace('!', '')
        element['patterns'][i] = element['patterns'][i].replace('[', '')
        element['patterns'][i] = element['patterns'][i].replace(']', '')
        element['patterns'][i] = element['patterns'][i].replace(',', '')

for element in data['intents']:
    for i in range(0, len(element['responses'])):
        element['responses'][i] = element['responses'][i].lower()
        element['responses'][i] = element['responses'][i].replace('.', '')
        element['responses'][i] = element['responses'][i].replace('?', '')
        element['responses'][i] = element['responses'][i].replace('!', '')
        element['responses'][i] = element['responses'][i].replace('[', '')
        element['responses'][i] = element['responses'][i].replace(']', '')
        element['responses'][i] = element['responses'][i].replace(',', '')


with open('../new_version/result_data_set.json', 'w', encoding='UTF-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
