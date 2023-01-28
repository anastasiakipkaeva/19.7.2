from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_auth_key_for_empty_reg_fields(email='', password=''):
    '''Доступ к веб приложению без ввода адреса электронной почты и пароля.
     Запрос API на возврат статуса 403 в связи с отсутствием в запросе данных пользователя'''

    # Отправляем запрос и сохраняем ответ с кодом статуса в status, а текст в result
    status, result = pf.get_api_key(email, password)

    # Сверяем ожидаемый и фактический результат
    assert status == 403
    print(result)


def test_get_api_key_for_not_valid_user(email=valid_email, password=invalid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403
    print('Неверно указан логин или пароль')


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result
    print('Ключ:', result)


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0





def test_add_new_pet_with_valid_data_without_photo(name='Мяу', animal_type='Кошара',
                                                   age='2'):
    """Проверяем что можно добавить питомца с корректными данными без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


def test_add_new_empty_pet(name='', animal_type='', age=''):
    '''Проверка добавления нового питомца без данных.'''

    # Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age
    print(result)


def test_add_new_pet_invalid_age(name='Жираф', animal_type='млекопитающие', age='999'):
    '''Проверка добавления нового питомца без фото с некорректными данными возраста.'''

    # Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['age'] != 0
    print(result)


def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Терминатор", "кот", "3", "images/Р1040103.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    print('ID удаляемого питомца:', pet_id)
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info_pet_id(name='Мышка', animal_type='крыса', age=9):
    """Проверяем возможность обновления информации о питомце с несуществующим pet_id"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Пробуем обновить  имя, тип и возраст при несуществующем id питомца
    pet_id = 'pet'
    status, result = pf.update_pet_info(auth_key, pet_id, name, animal_type, age)

    # Проверяем что статус ответа = 400 и такого питомца не существует
    assert status == 400
    print('Предоставленные данные не верны. Проверьте правильность написания pet_id')

def test_get_auth_key_with_invalid_key(filter="my_pets"):
    """ Проверяем, что запрос "моих питомцев" при запросе с неверно указанным ключом ничего не возвращает """
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets({'key': '555'}, filter)
    assert status == 403
    print(result)




