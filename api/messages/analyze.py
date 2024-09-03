import spacy
from asgiref.sync import sync_to_async
from textanalysis.models import ObjectKeyword, ActionVerb

nlp = spacy.load("en_core_web_sm")

async def find_object(sentence):
    doc = nlp(sentence)
    object_info = []
    action_info = []

    for token in doc:
        # Check for action verbs (verbs with certain dependency roles)
        if token.pos_ == "VERB" and token.dep_ in {"ROOT", "xcomp"}:
            action_text = token.text.lower()

            # Function to check for exact match or synonym in ActionVerb
            @sync_to_async
            def check_action_verb(word):
                try:
                    # Check for exact match
                    action_verb = ActionVerb.objects.get(verb__iexact=word)
                    return action_verb, False
                except ActionVerb.DoesNotExist:
                    # Check for synonyms
                    synonyms = ActionVerb.objects.all()
                    for av in synonyms:
                        if nlp(av.verb)[0].similarity(nlp(word)[0]) > 0.5:  # Adjust threshold as needed
                            return av, True
                return None, False

            action_verb, is_synonym = await check_action_verb(action_text)

            if action_verb:
                action_info.append({
                    'text': action_text,
                    'verb': action_verb.verb,
                    'id': action_verb.identifier,
                    'is_known': True,
                    'is_synonym': is_synonym
                })
            else:
                action_info.append({
                    'text': action_text,
                    'verb': None,
                    'id': None,
                    'is_known': False,
                    'is_synonym': False
                })

        # Check for direct objects (dobj) and objects of prepositions (pobj)
        if token.dep_ in {"dobj", "pobj"}:
            object_text = token.text.lower()

            # Function to check for exact match or synonym in ObjectKeyword
            @sync_to_async
            def check_keyword(word):
                try:
                    # Check for exact match
                    keyword = ObjectKeyword.objects.get(keyword__iexact=word)
                    return keyword, False
                except ObjectKeyword.DoesNotExist:
                    # Check for synonyms
                    synonyms = ObjectKeyword.objects.all()
                    for kw in synonyms:
                        if nlp(kw.keyword)[0].similarity(nlp(word)[0]) > 0.7:  # Adjust threshold as needed
                            return kw, True
                return None, False

            keyword, is_synonym = await check_keyword(object_text)

            if keyword:
                object_info.append({
                    'text': object_text,
                    'keyword': keyword.keyword,
                    'id': keyword.identifier,
                    'is_known': True,
                    'is_synonym': is_synonym
                })
            else:
                object_info.append({
                    'text': object_text,
                    'keyword': None,
                    'id': None,
                    'is_known': False,
                    'is_synonym': False
                })

    return {
        'actions': action_info,
        'objects': object_info
    }
