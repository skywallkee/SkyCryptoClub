# Tasks:
- [x] Refactor Profile Dashboard
- - currently, user's profile method differs from other user's profile method
- - merge both methods into one, so that both, currently logged in user and other user's profiles are in one method

- [ ] Refactor Profile Code @urgent
- - check index/profile/settings methods and refactor them
- - splitting should include:
- - - splitting methods into multiple more appropriate one-purpose functions
- - - rethinking logic for a better readability
- - - reducing the complexity as much as possible for a faster computing
- - - promoting reusability for other methods
- - - describing methods with appropriate comments for better understanding

- [ ] User Language @soon
- - add language field to User model with English as default
- - make mesages in a GLOBAL messages file
- - each language message should be of the form: VARIABLE_TITLLE = {"LANGUAGE": {"message": message}}
- - EXAMPLE: HELLO_WORLD = {"en": {"message": "Hello World"}, "de": {"message": "Hello Welt"}}