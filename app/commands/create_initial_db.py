from loguru import logger
from sqlalchemy import delete, func, select

from commands.command import Command
from db.database import get_db_session, transaction
from db.tables import Question, QuestionAnswer, QuestionTopic, QuestionType, Quiz, QuizAttempt, QuizType, User
from resources.schema_constants import QuizTypeName
from tests.factories import (
    QuestionFactory,
    QuestionTopicFactory,
    QuestionTypeFactory,
    QuizFactory,
    QuizTypeFactory,
    UserFactory,
)


class CreateInitialDB(Command):
    _select_from_models = tuple(
        [Question, Quiz, QuestionTopic, QuestionType, User, QuizAttempt, QuestionAnswer, QuizType]
    )

    async def run(self) -> None:
        async with get_db_session() as session:
            async with transaction(session=session):
                for model in self._select_from_models:
                    result = await session.execute(select(func.count()).select_from(model))
                    logger.info(f"В модели {model.__name__} {result.scalar()} записей.")

                objects = []

                personality_test_type = QuizTypeFactory.build(name="TEST PersonalityTest")
                personality_character_test_type = QuizTypeFactory.build(name=QuizTypeName.PERSONALITY_CHARACTER)
                personality_apprecation_test_type = QuizTypeFactory.build(name=QuizTypeName.PERSONALITY_APPRECATION)
                personality_values_test_type = QuizTypeFactory.build(name=QuizTypeName.PERSONALITY_VALUES)

                persona_test = QuizFactory.build(name="TEST Тест личности", parent=None, type=personality_test_type)
                character_test = QuizFactory.build(
                    name="TEST Тест характера личности", parent=persona_test, type=personality_character_test_type
                )
                apprecation_test = QuizFactory.build(
                    name="TEST Тест на языки признательности",
                    parent=persona_test,
                    type=personality_apprecation_test_type,
                )
                values_test = QuizFactory.build(
                    name="TEST Тест на ценности", parent=persona_test, type=personality_values_test_type
                )

                character_topic_openness = QuestionTopicFactory.build(name="TEST Открытость")
                character_topic_consciousness = QuestionTopicFactory.build(name="TEST Сознательность")
                character_topic_extraversion = QuestionTopicFactory.build(name="TEST Экстраверсия")
                character_topic_goodwill = QuestionTopicFactory.build(name="TEST Доброжелательность")
                character_topic_neuroticism = QuestionTopicFactory.build(name="TEST Невротичность")

                apprecation_topic_words = QuestionTopicFactory.build(name="TEST Слова поощрения")
                apprecation_topic_gifts = QuestionTopicFactory.build(name="TEST Подарки")
                apprecation_topic_help = QuestionTopicFactory.build(name="TEST Помощь")
                apprecation_topic_touch = QuestionTopicFactory.build(name="TEST Прикосновения")
                apprecation_topic_time = QuestionTopicFactory.build(name="TEST Время")

                values_topic_love = QuestionTopicFactory.build(name="TEST Любовь")
                values_topic_service = QuestionTopicFactory.build(name="TEST Услуги")
                values_topic_status = QuestionTopicFactory.build(name="TEST Статус")
                values_topic_money = QuestionTopicFactory.build(name="TEST Деньги")
                values_topic_things = QuestionTopicFactory.build(name="TEST Вещи")
                values_topic_information = QuestionTopicFactory.build(name="TEST Информация")

                character_question_type = QuestionTypeFactory.build(
                    name="TEST Выбор значения от 1 до 5 без значения по умолчанию",
                    params={
                        "required": True,
                        "default": None,
                        "multiple_answers": False,
                        "answer_type": "integer",
                        "min_value": 1,
                        "max_value": 5,
                    },
                )
                apprecation_question_type = QuestionTypeFactory.build(
                    name="TEST Булевый с нет по умолчанию",
                    params={
                        "required": False,
                        "default": False,
                        "multiple_answers": False,
                        "answer_type": "boolean",
                    },
                )
                values_question_type = QuestionTypeFactory.build(
                    name="TEST Выбор значения от 0 до 2 без значения по умолчанию",
                    params={
                        "required": True,
                        "default": None,
                        "multiple_answers": False,
                        "answer_type": "integer",
                        "min_value": 0,
                        "max_value": 2,
                    },
                )

                character_questions_texts_topics = [
                    ["Я очень любопытный", character_topic_openness],
                    ["Я люблю пробовать новое", character_topic_openness],
                    ["Я люблю приключения", character_topic_openness],
                    ["Я склонен к мечтательности", character_topic_openness],
                    ["Меня считают непрактичным", character_topic_openness],
                    ["Я организованный человек", character_topic_consciousness],
                    ["Для меня важны детали", character_topic_consciousness],
                    ["Я люблю составлять списки дел", character_topic_consciousness],
                    ["Я люблю составлять расписания", character_topic_consciousness],
                    ["Я перфекционист", character_topic_consciousness],
                    ["Я очень разговорчивый", character_topic_extraversion],
                    ["Я обычно первым начинаю беседу", character_topic_extraversion],
                    ["Я смело высказываю свое мнение", character_topic_extraversion],
                    ["Я чувствую прилив сил и вдохновение, когда нахожусь среди людей", character_topic_extraversion],
                    ["Я произвожу впечатление человека самоуверенного", character_topic_extraversion],
                    ["Я легко нахожу общий язык с другими людьми", character_topic_goodwill],
                    ["Я привык доверять окружающим", character_topic_goodwill],
                    ["Я люблю быть в команде", character_topic_goodwill],
                    ["Я не способен ответить отказом на просьбу", character_topic_goodwill],
                    ["Я произвожу впечатление пассивного человека", character_topic_goodwill],
                    ["Меня постоянно грызут сомнения", character_topic_neuroticism],
                    ["Я часто угрюм", character_topic_neuroticism],
                    ["Я очень чувствителен", character_topic_neuroticism],
                    ["Я произвожу впечатление чересчур эмоционального человека", character_topic_neuroticism],
                    ["Я легко меняю взгляды", character_topic_neuroticism],
                ]

                for character_questions_text, character_questions_topic in character_questions_texts_topics:
                    objects.append(
                        QuestionFactory.build(
                            text=f"TEST {character_questions_text}",
                            quiz=character_test,
                            type=character_question_type,
                            topic=character_questions_topic,
                        )
                    )

                apprecation_question_texts_topics = [
                    ["Мне нравится получать записки со словами поддержки", apprecation_topic_words],
                    ["Мне важно слышать комплименты", apprecation_topic_words],
                    ["Я люблю оставлять записочки друзьям или возлюбленным", apprecation_topic_words],
                    ["Мне нравится, когда мне дарят подарки", apprecation_topic_gifts],
                    [
                        "Мне очень приятно, когда кто-то помнит о важных для меня датах и делает подарок",
                        apprecation_topic_gifts,
                    ],
                    ["Я люблю привозить друзьям сувениры из путешествий", apprecation_topic_gifts],
                    ["Я ощущаю заботу, когда друг мне помогает", apprecation_topic_help],
                    [
                        "Я ощущаю признательность, когда коллега предлагает помощь с проектом или отдельным заданием",
                        apprecation_topic_help,
                    ],
                    [
                        "Я предпочту приготовить десерт другу или возлюбленному (одному или вместе), чем купить готовый",
                        apprecation_topic_help,
                    ],
                    ["Мне нравится, когда меня обнимают", apprecation_topic_touch],
                    [
                        "Я чувствую, что меня ценят, когда человек, который мне дорог, обнимает меня",
                        apprecation_topic_touch,
                    ],
                    ["Мне удобно дотрагиваться до руки собеседника во время беседы", apprecation_topic_touch],
                    ["Мне нравится встречаться с друзьями небольшими компаниями", apprecation_topic_time],
                    ["Я ощущаю близость, когда делаю что-то вместе с кем-то", apprecation_topic_time],
                    [
                        "Я люблю навещать друзей если проезжаю мимо хотя бы на 5 минут, нередко связываться хотя бы на короткое время",
                        apprecation_topic_time,
                    ],
                ]

                for apprecation_question_text, apprecation_question_topic in apprecation_question_texts_topics:
                    objects.append(
                        QuestionFactory.build(
                            text=f"TEST {apprecation_question_text}",
                            quiz=apprecation_test,
                            type=apprecation_question_type,
                            topic=apprecation_question_topic,
                        )
                    )

                values_question_texts_topics = [
                    ["Мне важно чувствовать одобрение", values_topic_love],
                    ["Мне важно нравиться окружающим", values_topic_love],
                    ["Мне важно чувствовать себя частью группы", values_topic_love],
                    ["Мне важно чувствовать, что близкие меня поддерживают", values_topic_service],
                    ["Я чувствую себя особенным, когда кто-то оказывает мне услугу", values_topic_service],
                    ["Мне важно чувствовать заботу окружающих", values_topic_service],
                    ["Я чувствую себя потрясающе, когда меня хвалят", values_topic_status],
                    ["Мне нравится руководить людьми", values_topic_status],
                    ["Мне важно чувствовать уважение", values_topic_status],
                    ["Для меня важна финансовая стабильность", values_topic_money],
                    ["Я работаю в основном ради денег", values_topic_money],
                    ["Я уверен, что деньги необходимы, чтобы быть абсолютно счастливым", values_topic_money],
                    ["Мне нравится собирать какие-то вещи", values_topic_things],
                    ["Я часто покупаю подарки, делаю презенты", values_topic_things],
                    [
                        "Я могу вспомнить много вещей дома, которые имеют особое эмоциональное значение",
                        values_topic_things,
                    ],
                    ["Мне нравится быть в курсе происходящего", values_topic_information],
                    ["Мне нравится давать советы", values_topic_information],
                    ["Мне нравится учить и учиться", values_topic_information],
                ]

                for values_question_text, values_question_topic in values_question_texts_topics:
                    objects.append(
                        QuestionFactory.build(
                            text=f"TEST {values_question_text}",
                            quiz=values_test,
                            type=values_question_type,
                            topic=values_question_topic,
                        )
                    )

                user = UserFactory.build(tg_user_id=-1)
                objects.append(user)

                objects.append(personality_test_type)
                objects.append(persona_test)
                objects.append(character_test)
                objects.append(apprecation_test)
                objects.append(values_test)
                objects.append(character_topic_consciousness)
                objects.append(character_topic_extraversion)
                objects.append(character_topic_goodwill)
                objects.append(character_topic_neuroticism)
                objects.append(character_topic_openness)
                objects.append(apprecation_topic_gifts)
                objects.append(apprecation_topic_help)
                objects.append(apprecation_topic_time)
                objects.append(apprecation_topic_touch)
                objects.append(apprecation_topic_words)
                objects.append(values_topic_information)
                objects.append(values_topic_love)
                objects.append(values_topic_money)
                objects.append(values_topic_service)
                objects.append(values_topic_status)
                objects.append(values_topic_things)
                objects.append(character_question_type)
                objects.append(apprecation_question_type)
                objects.append(values_question_type)

                session.add_all(objects)

                await session.flush()

                for model in self._select_from_models:
                    result = await session.execute(select(func.count()).select_from(model))
                    logger.info(f"В модели {model.__name__} теперь {result.scalar()} записей.")

    async def unrun(self) -> None:
        async with get_db_session() as session:
            async with transaction(session=session):

                for model in self._select_from_models:
                    result = await session.execute(select(func.count()).select_from(model))
                    logger.info(f"В модели {model.__name__} {result.scalar()} записей.")

                stmt = select(Quiz.uuid).where(Quiz.name.startswith("TEST"))
                result = await session.execute(stmt)
                test_quiz_ids = result.scalars().all()

                stmt = select(QuizAttempt.uuid).where(QuizAttempt.quiz_id.in_(test_quiz_ids))
                result = await session.execute(stmt)
                test_quiz_attempt_ids = result.scalars().all()

                statements = [
                    delete(QuestionAnswer).where(QuestionAnswer.attempt_id.in_(test_quiz_attempt_ids)),
                    delete(QuizAttempt).where(QuizAttempt.quiz_id.in_(test_quiz_ids)),
                    delete(Question).where(Question.text.startswith("TEST")),
                    delete(QuestionType).where(QuestionType.name.startswith("TEST")),
                    delete(QuestionTopic).where(QuestionTopic.name.startswith("TEST")),
                    delete(Quiz).where(Quiz.name.startswith("TEST")),
                    delete(QuizType).where(QuizType.name.startswith("TEST")),
                    delete(User).where(User.tg_user_id < 0),
                ]
                for statement in statements:
                    await session.execute(statement)

                await session.flush()

                for model in self._select_from_models:
                    result = await session.execute(select(func.count()).select_from(model))
                    logger.info(f"В модели {model.__name__} теперь {result.scalar()} записей.")


if __name__ == "__main__":
    command = CreateInitialDB()
    command.run_cli()
