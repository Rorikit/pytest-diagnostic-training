import allure


class MockRedisClient:
    def ping(self) -> bool:
        raise ConnectionError("Redis mock unavailable: connection refused on redis://localhost:6379")


def test_api_ui_members_sync_failure():
    with allure.step("API GET /redfish/v1/Chassis вернул HTTP 200"):
        api_members = [
            {"@odata.id": "/redfish/v1/Chassis/1"},
            {"@odata.id": "/redfish/v1/Chassis/2"},
        ]

    with allure.step("Получение Members из Web UI"):
        ui_members = [
            {"@odata.id": "/redfish/v1/Chassis/1"},
            {"@odata.id": "/redfish/v1/Chassis/3"},
        ]

    with allure.step("Сравнение API Members и UI Members"):
        assert api_members == ui_members


def test_backend_api_500_failure():
    with allure.step("API POST /orders вернул HTTP 500"):
        response = {"status_code": 500, "body": {"error": "internal"}}
        assert response["status_code"] < 500


def test_auth_forbidden_failure():
    with allure.step("Login под readonly-сессией"):
        user = {"role": "readonly", "token": "mock-token"}
        assert user["token"]

    with allure.step("API DELETE /users/42 вернул HTTP 403"):
        response = {"status_code": 403}
        assert response["status_code"] == 204


def test_ui_timeout_failure():
    with allure.step("Ожидание Web UI страницы Dashboard timeout 30s"):
        page_loaded = False
        assert page_loaded is True


def test_dependency_connection_failure():
    redis = MockRedisClient()

    with allure.step("Проверка Redis mock dependency: redis://localhost:6379 недоступен"):
        assert redis.ping() is True
