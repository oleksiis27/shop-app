# Контекст проекта

Я QA Automation Engineer, строю портфолио для позиции Senior/Strong Middle+ QA.
У меня есть e-commerce сервис (shop-app), и я создаю для него AQA-фреймворк на Java.

Сервис запускается через Docker Compose и доступен на `http://localhost:8000`.
Запуск: в директории shop-app выполнить `docker-compose up --build -d`.

---

## Стек тест-фреймворка

- **Java 21**
- **Gradle** (Kotlin DSL)
- **JUnit 5** — тест-раннер
- **REST Assured** — API-тесты
- **Allure** — отчёты
- **AssertJ** — читаемые ассерты
- **Jackson** — сериализация/десериализация JSON
- **Faker (Java)** — генерация тестовых данных
- **Owner** — конфигурация (base URL, credentials)

---

## Структура проекта

```
shop-tests-java/
├── src/
│   ├── main/java/com/shop/
│   │   ├── config/
│   │   │   └── AppConfig.java          # Owner-интерфейс для конфигурации
│   │   ├── models/
│   │   │   ├── User.java               # POJO для User
│   │   │   ├── Product.java            # POJO для Product
│   │   │   ├── Category.java           # POJO для Category
│   │   │   ├── CartItem.java           # POJO для CartItem
│   │   │   ├── Cart.java               # POJO для Cart (items + total)
│   │   │   ├── Order.java              # POJO для Order
│   │   │   ├── OrderItem.java          # POJO для OrderItem
│   │   │   ├── TokenResponse.java      # POJO для login response
│   │   │   └── PaginatedResponse.java  # POJO для paginated response
│   │   ├── api/
│   │   │   ├── AuthApi.java            # REST Assured спецификации для /api/auth/*
│   │   │   ├── ProductApi.java         # для /api/products/*
│   │   │   ├── CategoryApi.java        # для /api/categories
│   │   │   ├── CartApi.java            # для /api/cart/*
│   │   │   └── OrderApi.java           # для /api/orders/* и /api/admin/orders/*
│   │   └── helpers/
│   │       ├── AuthHelper.java         # получение токена, создание юзера
│   │       └── TestDataHelper.java     # генерация тестовых данных через Faker
│   └── test/java/com/shop/tests/
│       ├── auth/
│       │   └── AuthTests.java
│       ├── products/
│       │   └── ProductTests.java
│       ├── cart/
│       │   └── CartTests.java
│       └── orders/
│           └── OrderTests.java
├── src/main/resources/
│   └── app.properties                  # base.url, admin.email, admin.password, etc.
├── build.gradle.kts
├── settings.gradle.kts
├── .github/
│   └── workflows/
│       └── tests.yml                   # CI: поднять shop-app, запустить тесты
└── README.md
```

---

## API сервиса (полная спецификация)

Base URL: `http://localhost:8000`

### Auth
- `POST /api/auth/register` — body: `{ email, password, name }` → 201 UserResponse
- `POST /api/auth/login` — body: `{ email, password }` → 200 `{ access_token, token_type }`
- `GET /api/auth/me` — Header: `Authorization: Bearer <token>` → 200 UserResponse

UserResponse: `{ id, email, name, role, created_at }`

### Products
- `GET /api/products` — query params: `page, limit, category, search, sort_by, min_price, max_price` → 200 `{ items: Product[], total, page, limit, pages }`
- `GET /api/products/{id}` → 200 Product
- `POST /api/products` — admin only, body: `{ name, description, price, stock, category_id, image_url }` → 201 Product
- `PUT /api/products/{id}` — admin only, body: partial product → 200 Product
- `DELETE /api/products/{id}` — admin only → 204

Product: `{ id, name, description, price, stock, category_id, category: Category, image_url, created_at }`

### Categories
- `GET /api/categories` → 200 Category[]

Category: `{ id, name, slug }`

### Cart (требует авторизацию)
- `GET /api/cart` → 200 `{ items: CartItem[], total }`
- `POST /api/cart/items` — body: `{ product_id, quantity }` → 201 CartItem
- `PUT /api/cart/items/{id}` — body: `{ quantity }` → 200 CartItem
- `DELETE /api/cart/items/{id}` → 204
- `DELETE /api/cart` → 204

CartItem: `{ id, product_id, quantity, product: { id, name, price, image_url } }`

### Orders (требует авторизацию)
- `POST /api/orders` — создаёт заказ из корзины → 201 Order
- `GET /api/orders` — список заказов текущего пользователя → 200 Order[]
- `GET /api/orders/{id}` — детали заказа → 200 Order
- `GET /api/admin/orders` — admin only, все заказы → 200 Order[]
- `PUT /api/admin/orders/{id}/status` — admin only, body: `{ status }` → 200 Order

Order: `{ id, user_id, status, total, created_at, items: OrderItem[] }`
OrderItem: `{ id, product_id, quantity, price, product: { id, name, image_url } }`

Статусы заказа: pending → confirmed → shipped → delivered | cancelled
Невалидные переходы возвращают 400.

### Коды ответов
- 200 — успех
- 201 — создано
- 204 — удалено (без тела)
- 400 — невалидные данные
- 401 — не авторизован / невалидный токен
- 403 — нет прав (не admin)
- 404 — не найдено
- 409 — конфликт (email уже занят)
- 422 — ошибка валидации (Pydantic)

### Тестовые пользователи (seed)
- Admin: `admin@shop.com` / `admin123`
- User: `user@shop.com` / `user123`

### Seed данные
- 6 категорий: Electronics, Clothing, Books, Home & Garden, Sports, Toys
- 60 товаров (по 10 на категорию)

---

## Какие тесты написать

### AuthTests
- Регистрация нового пользователя → 201, проверить поля ответа
- Регистрация с уже существующим email → 409
- Логин с правильными credentials → 200, access_token не пустой
- Логин с неправильным паролем → 401
- GET /me с валидным токеном → 200, правильный user
- GET /me без токена → 403
- GET /me с невалидным токеном → 401

### ProductTests
- Получить список продуктов → 200, items не пустой, пагинация корректна
- Фильтрация по категории → все товары из нужной категории
- Поиск по имени → результаты содержат search term
- Сортировка по цене (asc/desc) → порядок правильный
- Получить продукт по ID → 200, все поля присутствуют
- Получить несуществующий продукт → 404
- Создать продукт (admin) → 201
- Создать продукт (user) → 403
- Создать продукт без авторизации → 403
- Обновить продукт (admin) → 200, поля обновлены
- Удалить продукт (admin) → 204
- Удалить несуществующий продукт → 404

### CartTests
- Добавить товар в корзину → 201
- Получить корзину → items содержит добавленный товар, total корректный
- Добавить тот же товар повторно → quantity увеличивается
- Обновить количество → 200, новый quantity
- Удалить товар из корзины → 204
- Очистить корзину → 204, после GET корзина пустая
- Добавить товар без авторизации → 403

### OrderTests
- Оформить заказ (из непустой корзины) → 201, status=pending, total корректный
- Оформить заказ из пустой корзины → 400
- После оформления корзина пустая
- Получить список заказов → содержит созданный заказ
- Получить заказ по ID → 200, все поля
- Получить чужой заказ → 404
- Admin: получить все заказы → 200
- Admin: изменить статус pending → confirmed → 200
- Admin: невалидный переход статуса → 400
- User: попытка изменить статус → 403

---

## Важные требования

1. Каждый тестовый класс должен быть независимым — тесты не зависят друг от друга
2. Используй `@BeforeEach` / `@BeforeAll` для подготовки данных
3. Для тестов корзины и заказов — создавай fresh пользователя через register для изоляции
4. Allure-аннотации: `@Epic`, `@Feature`, `@Story`, `@Severity`, `@Description`
5. API-классы используют REST Assured RequestSpecification с базовым URL из конфига
6. Все тесты должны проходить при чистом запуске сервиса (после docker-compose up)
7. GitHub Actions CI: клонирует shop-app, поднимает docker-compose, ждёт health, запускает тесты, сохраняет Allure-отчёт как артефакт

---

## Задача

Реализуй этот тест-фреймворк пошагово:
1. Инициализируй Gradle-проект, настрой build.gradle.kts со всеми зависимостями
2. Создай конфигурацию (Owner) и POJO-модели
3. Создай API-классы (REST Assured спецификации)
4. Создай хелперы (AuthHelper, TestDataHelper)
5. Напиши AuthTests
6. Напиши ProductTests
7. Напиши CartTests
8. Напиши OrderTests
9. Настрой GitHub Actions CI
10. Создай README.md

Делай по одному шагу за раз. После каждого шага спрашивай, готов ли я двигаться дальше.
