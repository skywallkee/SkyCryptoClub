# Tasks:
- [x] Create Contact Page
- - for both, logged in and not logged in users
- - form that will send a mail to contact@skycrypto.club
- - should not replace support tickets!
- - the main purpose will be for users that can't login/have account problems and for partners

- [x] Add Partners Banner to Index
- - add banners for mobile, tablet and desktop
- - banners should be responsive to window resize
- - banners should change after each refresh

- [x] Refactor Profile Dashboard
- - currently, user's profile method differs from other user's profile method
- - merge both methods into one, so that both, currently logged in user and other user's profiles are in one method

- [x] Refactor Profile Code @urgent
- - check index/profile/settings methods and refactor them
- - splitting should include:
- - - splitting methods into multiple more appropriate one-purpose functions
- - - rethinking logic for a better readability
- - - reducing the complexity as much as possible for a faster computing
- - - promoting reusability for other methods
- - - describing methods with appropriate comments for better understanding

- [ ] Create Exchanges
- - Request Exchange
- - - Users can make a new request and set the wanted rate
- - View Exchange List
- - - Users can view all the requests that are opened
- - - Users can filter all the requests based on the given criteria (currency, min amount, max amount, ratio)
- - Exchange History
- - - Users can view all their past exchanges

- [ ] Create Support Page
- - Support Ticket
- - - Users can open/close/reply to their support tickets regarding a given problem
- - - Support staff can reply to support tickets assigned to their field of expertise
- - - Support staff can mark a ticket as answered

- [ ] User Language @soon
- - add language field to User model with English as default
- - make mesages in a GLOBAL messages file
- - each language message should be of the form: VARIABLE_TITLLE = {"LANGUAGE": {"message": message}}
- - EXAMPLE: HELLO_WORLD = {"en": {"message": "Hello World"}, "de": {"message": "Hello Welt"}}

- [ ] Create Messages File @soon
- - create a MESSAGES.py that contains dictionaries with each messages that are being sent
- - this will allow messages to be modified easily from one file (allowing translation too)