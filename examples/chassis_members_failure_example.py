import allure


def test_chassis_members_should_be_equal():
    with allure.step("Логин под admin-сессией"):
        session_created = True
        assert session_created is True

    with allure.step("API GET /redfish/v1/Chassis вернул HTTP 200"):
        api_response = {
            "Members": [
                {"@odata.id": "/redfish/v1/Chassis/1"},
                {"@odata.id": "/redfish/v1/Chassis/2"},
            ]
        }
        api_members = api_response["Members"]

    with allure.step("Получение Members из Web UI"):
        ui_members = [
            {"@odata.id": "/redfish/v1/Chassis/1"},
            {"@odata.id": "/redfish/v1/Chassis/3"},
        ]

    with allure.step("Сравнение API Members и UI Members"):
        assert api_members == ui_members
