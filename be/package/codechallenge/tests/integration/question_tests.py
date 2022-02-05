from codechallenge.entities import Question, Questions


class TestCaseQuestionEP:
    def t_unexistentQuestion(self, testapp):
        testapp.get("/question/30", status=404)

    def t_fetchingSingleQuestion(self, testapp):
        question = Question(text="Text", position=0).save()
        response = testapp.get(f"/question/{question.uid}", status=200)
        assert response.json["text"] == "Text"
        assert response.json["answers"] == []

    def t_createNewQuestion(self, testapp):
        # CSRF token is needed also in this case
        response = testapp.post_json(
            "/question/new",
            {
                "text": "eleven pm",
                "code": "x = 0; x += 1; print(x)",
                "position": 2,
            },
            status=200,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )
        assert Questions.count() == 1
        assert response.json["text"] == "eleven pm"
        assert response.json["position"] == 2

    def t_changeTextAndPositionOfAQuestion(self, testapp):
        question = Question(text="Text", position=0).save()
        response = testapp.patch_json(
            f"/question/edit/{question.uid}",
            {
                "text": "Edited text",
                "position": 2,
            },
            status=200,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )

        assert response.json["text"] == "Edited text"
        assert response.json["position"] == 2

    def t_editingUnexistentQuestion(self, testapp):
        # the empty dictionary is still needed to prevent a
        # json.decoder.JSONDecodeError
        testapp.patch_json(
            "/question/edit/40",
            {},
            status=404,
            headers={"X-CSRF-Token": testapp.get_csrf_token()},
        )
