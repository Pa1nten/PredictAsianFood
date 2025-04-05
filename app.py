from flask import Flask, request, render_template
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from PIL import Image
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'

model = load_model("full_model.h5")

index_to_label = {
    0: 'Moti',
    1: 'Onigiri',
    2: 'Ramen',
    3: 'Sukiyaki',
    4: 'Sup miso',
    5: 'Takoyaki',
    6: 'Tempura',
    7: 'Yakiniku',
    8: 'Yakitori'
}

recipes = {
    'Moti': {
        'ingredients': [
            '1 чашка сладкой рисовой муки (мочико)',
            '1 чашка воды',
            '1/4 чашки сахара',
            'Кукурузный крахмал для посыпки'
        ],
        'steps': [
            'Смешайте рисовую муку, воду и сахар в миске до однородности.',
            'Накройте миску пленкой и нагревайте в микроволновке 1 минуту. Перемешайте и повторяйте процесс до получения липкого теста.',
            'Посыпьте поверхность кукурузным крахмалом, выложите тесто и сформируйте небольшие шарики или лепешки.'
        ],
        'source': 'https://tastesbetterfromscratch.com/mochi-ice-cream/?utm_source=chatgpt.com'
    },
    'Onigiri': {
        'ingredients': [
            '2 чашки вареного японского риса',
            'Начинка по вкусу (например, лосось, маринованные сливы)',
            'Листы нори, разрезанные на полоски',
            'Соль по вкусу'
        ],
        'steps': [
            'Смочите руки водой, возьмите немного соли и сформируйте из риса треугольник или шарик, добавив внутрь начинку.',
            'Заверните рисовый шарик полоской нори.'
        ],
        'source': 'https://www.justonecookbook.com/onigiri-rice-balls/?utm_source=chatgpt.com'
    },
    'Ramen': {
        'ingredients': [
            '1 ст. л. кунжутного масла',
            '3 ч. л. тертого имбиря',
            '4 ч. л. тертого чеснока',
            '4 чашки бульона (куриного или овощного)',
            '2 упаковки лапши для рамена',
            'Овощи и белки по вкусу (например, шпинат, грибы, вареное яйцо)'
        ],
        'steps': [
            'Обжарьте имбирь и чеснок на кунжутном масле до аромата.',
            'Добавьте бульон и доведите до кипения.',
            'Варите лапшу в бульоне согласно инструкции.',
            'Добавьте овощи и другие ингредиенты, подавайте горячим.'
        ],
        'source': 'https://pinchofyum.com/quick-homemade-ramen?utm_source=chatgpt.com'
    },
    'Sukiyaki': {
        'ingredients': [
            'Тонко нарезанная говядина',
            'Тофу',
            'Лук-порей',
            'Шиитаке',
            'Соус (смешайте соевый соус, мирин, сахар и саке)'
        ],
        'steps': [
            'Обжарьте говядину в сковороде.',
            'Добавьте овощи и тофу.',
            'Влейте соус и тушите до готовности.'
        ],
        'source': 'https://www.justonecookbook.com/sukiyaki/?utm_source=chatgpt.com'
    },
    'Sup miso': {
        'ingredients': [
            '4 чашки даси',
            '3 ст. л. мисо-пасты',
            'Тофу, водоросли вакаме, зеленый лук'
        ],
        'steps': [
            'Нагрейте даси, не доводя до кипения.',
            'Разведите мисо-пасту в небольшом количестве даси и добавьте в кастрюлю.',
            'Добавьте тофу и вакаме, прогрейте и подавайте.'
        ],
        'source': 'https://www.justonecookbook.com/homemade-miso-soup/?utm_source=chatgpt.com'
    },
    'Tempura': {
        'ingredients': [
            '1 яйцо',
            '1 чашка ледяной воды',
            '1 чашка муки',
            'Морепродукты и овощи по выбору'
        ],
        'steps': [
            'Смешайте яйцо с ледяной водой, добавьте муку и перемешайте.',
            'Окуните ингредиенты в кляр и обжарьте во фритюре.'
        ],
        'source': 'https://www.justonecookbook.com/tempura/?utm_source=chatgpt.com'
    },
    'Takoyaki': {
        'ingredients': [
            '1 чашка муки для тако-яки',
            '2 яйца',
            '2 чашки бульона',
            'Половина чашки тертого сыра',
            'Порезанные кальмары, кусочки темпуры'
        ],
        'steps': [
            'Смешайте муку, яйца и бульон, чтобы получить жидкое тесто.',
            'Разогрейте форму для такояки, налейте тесто, добавьте начинку и обжаривайте до золотистой корочки.'
        ],
        'source': 'https://www.justonecookbook.com/takoyaki/?utm_source=chatgpt.com'
    },
    'Yakiniku': {
        'ingredients': [
            'Тонко нарезанная говядина',
            'Соевый соус',
            'Мирин',
            'Терияки-соус'
        ],
        'steps': [
            'Замаринуйте говядину в соевом соусе, мирине и терияки.',
            'Обжаривайте мясо на гриле или сковороде до готовности.'
        ],
        'source': 'https://www.justonecookbook.com/yakiniku/?utm_source=chatgpt.com'
    },
    'Yakitori': {
        'ingredients': [
            'Куриные бедра или грудка',
            'Соевый соус',
            'Мирин',
            'Сахар',
            'Имбирь'
        ],
        'steps': [
            'Замаринуйте курицу в смеси соевого соуса, мирина, сахара и имбиря.',
            'Обжаривайте на гриле или сковороде до золотистой корочки.'
        ],
        'source': 'https://www.justonecookbook.com/yakitori/?utm_source=chatgpt.com'
    }
}

def smart_resize(img, target):
    base_width = img.width
    base_height = img.height
    target_width = target[0]
    target_height = target[1]

    width_first_way = round(target_height / base_height * base_width)

    if width_first_way < target_width:
        height_first_way = round(target_width / base_width * base_height)
        img = img.resize((target_width, height_first_way))
    else:
        img = img.resize((width_first_way, target_height))

    left = (img.width - target_width) // 2
    top = (img.height - target_height) // 2
    right = left + target_width
    bottom = top + target_height
    img = img.crop((left, top, right, bottom))

    return img

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            try:
                img = Image.open(filepath).convert("RGB")
                img = smart_resize(img, (160, 160))
                img_array = image.img_to_array(img)
                img_array = np.expand_dims(img_array, axis=0)
                img_array = img_array / 255.0

                prediction = model.predict(img_array)
                max_confidence = np.max(prediction)
                class_index = np.argmax(prediction)

                confidence_threshold = 0.6

                if max_confidence < confidence_threshold:
                    label = 'Не удалось распознать блюдо'
                    recipe = 'Попробуйте загрузить другое изображение. Убедитесь, что блюдо хорошо видно и не размыто.'
                else:
                    label = index_to_label.get(class_index, 'Неизвестное блюдо')
                    recipe = recipes.get(label, "Рецепт не найден.")
            except Exception as e:
                label = 'Ошибка при обработке изображения'
                recipe = str(e)

            return render_template('index.html', label=label, recipe=recipe, image=file.filename)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False,host ='',port ='')
