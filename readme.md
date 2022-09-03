ECF - personal expense tracker


This app was created as a personal skill-set test/revision of sorts, as well as
an item for a personal coding portfolio. 

Expense tracking seemed both as a useful/recyclable/upgradeable tool, as well as
an almost-ideal testing-ground for multiple challenges. In itself, it allows for solving
multiple different problems without repeating similar functionalities,
thus allowing for a diverse code content, while keeping the amount of code minimal, 
with a complex structure relative to the size of the app.

The idea was to allow for a specific type of querying and analyzing of expenses through
time, while keeping the interface basic but intuitive.

The app consists of two main functionalities - a calendar widget for querying existing
data, and the form for cost entries and entry editing. Querying is made via Ajax requests
where it is necessary to define the "time mode" of the query (day, week, whole month),
choose the dates, define number of results per page, as well as for which
currencies the results are being requested. It is also possible on top of that to query via the
item name and item category name.

The point was to allow for entering expenses in multiple currencies, but still be able to get the
total sum of costs if necessary, in addition to individual-currency queries. The user
has to define the "base-currency" when registering, which is actually the main referent
currency for the user. If the user enters expenses in any other currencies, those also
get converted to the main chosen currency (via an async API request via Celery to a website
that stores historical and current data for exchange rates), allowing for querying total costs both
in the original currency for the entries, and as the total costs in the main chosen
currency. If the user wishes to change the basic currency, all historical expenses data
also gets converted to the new chosen "base-currency", which makes it possible for the user
to keep track of all the costs in a custom and flexible manner.

For the individual articles/items it is necessary to define a "category", which helps
user make customized queries later on - for example, it is possible to create a category
"fruit" for apples and bananas, and subsequently see what the monthly costs (for instance)
for the fruits are. The sub-option for querying by item or category allows the user to see
the expenses for both "apples" and "fruit" in a certain time period.

It was a conscious decision not to use CSS/JS libraries and frameworks - most of the 
functionalities like pagination/modals/pop-up messages/autofill/auto-suggest
were written as VanillaJS, with custom CSS. The calendar widget is dynamically created 
from and relative to the JS Date object, while Flask-WTForms were mostly used for forms, as
an element of Flask. Flask-SQLalchemy was used with Postgres to store the data.

Since this app is a test of sorts in its nature, i.e. it does not have a larger purpose
apart from a certain personal "milestone", it is not completely polished and there
are certain functionalities which were kept in mind for this phase, but it was decided
that it would be an overkill to go that far, having the hermetic/temporary character
of this app in mind. On top of that, these functionalities are for the most part not
a new challenge within the app, but mostly a variation or a sub-option relative to the current level
of functionality. A couple of things that were considered: querying by a custom 
time-period or/and querying of all expenses ever made, table-sorting and search option
(although possibly superfluous, having in mind the Item/Category query which can 
be used to cherry-pick a certain element of interest), as well as saving the chosen
queries for browsing/analysis in the future. In addition to that, email logging 
of details of errors as well as a testing module for the app are-were foreseen
as the next steps to be made.

*The app is not completely optimized for mobile devices, but only to a degree for 
resizing events on a laptop/PC screen at the current moment.

















