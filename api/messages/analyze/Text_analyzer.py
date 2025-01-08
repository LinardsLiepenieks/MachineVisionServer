import spacy
from asgiref.sync import sync_to_async
from textanalysis.models import ObjectKeyword, ActionVerb


class TextAnalyzer:
    def __init__(self):
        """Initialize the TextAnalyzer with spaCy model."""
        self.nlp = spacy.load("en_core_web_sm")

    async def analyze_text(self, sentence: str) -> dict:
        """
        Analyze text to find objects and actions.

        Args:
            sentence (str): The input text to analyze

        Returns:
            dict: Dictionary containing lists of found actions and objects
        """
        doc = self.nlp(sentence)
        object_info = []
        action_info = []

        for token in doc:
            if token.pos_ == "VERB" and token.dep_ in {"ROOT", "xcomp"}:
                action = await self._process_action(token.text.lower())
                action_info.append(action)

            if token.dep_ in {"dobj", "pobj"}:
                object_item = await self._process_object(token.text.lower())
                object_info.append(object_item)

        output = {"actions": action_info, "objects": object_info}
        return output

    async def _process_action(self, action_text: str) -> dict:
        """Process a single action token."""
        action_verb, is_synonym = await self._check_action_verb(action_text)

        if action_verb:
            return {
                "text": action_text,
                "verb": action_verb.verb,
                "id": action_verb.identifier,
                "is_known": True,
                "is_synonym": is_synonym,
            }

        return {
            "text": action_text,
            "verb": None,
            "id": None,
            "is_known": False,
            "is_synonym": False,
        }

    async def _process_object(self, object_text: str) -> dict:
        """Process a single object token."""
        keyword, is_synonym = await self._check_keyword(object_text)

        if keyword:
            return {
                "text": object_text,
                "keyword": keyword.keyword,
                "id": keyword.identifier,
                "is_known": True,
                "is_synonym": is_synonym,
            }

        return {
            "text": object_text,
            "keyword": None,
            "id": None,
            "is_known": False,
            "is_synonym": False,
        }

    @sync_to_async
    def _check_action_verb(self, word: str) -> tuple:
        """
        Check if a word matches or is similar to known action verbs.

        Returns:
            tuple: (ActionVerb object or None, is_synonym boolean)
        """
        try:
            action_verb = ActionVerb.objects.get(verb__iexact=word)
            return action_verb, False
        except ActionVerb.DoesNotExist:
            synonyms = ActionVerb.objects.all()
            for av in synonyms:
                if self.nlp(av.verb)[0].similarity(self.nlp(word)[0]) > 0.5:
                    return av, True
        return None, False

    @sync_to_async
    def _check_keyword(self, word: str) -> tuple:
        """
        Check if a word matches or is similar to known object keywords.

        Returns:
            tuple: (ObjectKeyword object or None, is_synonym boolean)
        """
        try:
            keyword = ObjectKeyword.objects.get(keyword__iexact=word)
            return keyword, False
        except ObjectKeyword.DoesNotExist:
            synonyms = ObjectKeyword.objects.all()
            for kw in synonyms:
                if self.nlp(kw.keyword)[0].similarity(self.nlp(word)[0]) > 0.7:
                    return kw, True
        return None, False
