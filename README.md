# Dev-Support
Showcase your Project  | Sell your Scripts 


## Inspiration
We love Open Source, but wouldn’t it be great it to acknowledge the contributions of these generous soles, by helping them earn some cash, without burning a hole in your pocket ? That’s the whole point. Browse cool projects, and while the idea is free ;) the script behind is not. Pay no more than your regular coffee and access the scripts and use them to build your own cool project.

## What it does
It is basically a code marketplace where a developer gets to post his / her cool project and those who are interested in their idea or want to extend their idea, can pay a nominal fee to access the scripts.

## How we built it
1. Front-end : - Materialize Framework ( its cool !! ) All the card layouts you find on the app , courtesy to this easy to use framework. 
2. Backend :- Flask and Python with Jinja2 templating engine.
3. Payments were accepted using the stripe-api.
4. User credentials were fetched using the github api , and were stored in mongodb database provided by mongolabs.
5. The project details that you see are ddirectly converted from the developer supplied readme.MD document. We used strapdown.js for this. (outdated project -> but still got shit done for our web-app) 


## Challenges we ran into
1. JINJA2 → This needs a serious mention !! Awful way of binding model and view . (i repeat AWEFUL !!!! ). Had a hard time writing for and if’s for every html and css page. PATHETIC !! 
2. One more issue was fetching the avatar_url (github profile picture) from the heroku version of the app.I guess this feature is available only for enterprise github. On the contrary, the avatar_url worked perfectly for the version running on local host.

## Accomplishments that we're proud of
1. A working prototype of the proposed web-app.
2. Payment gateway and the script downloading works flawlessly.
3. We are proud of the app layout and have enjoyed the entire journey starting from ‘from flask import Flask’ to git commit -m “all done !! phew :) ”

## What we learned
1. A cool way to protect the download link to be visible to the buyer ( really cool ;) neat hack !! )
2. Implementing stripe api to accept payments
3. Using the gihub-api to fetch email , avatars , repos , location etc 
4. Connecting with mongolab to store user data
5. Deploying flask apps on heroku
6. DEBUGGING !! (couldn't have missed this :-> thanks to the weird jinja bugs !)

## What's next for Dev Support
We look forward to making the website more responsive and faster adhering to the best principles of design and structure. We also plan to enhance the security features of the site and look forward to including more login API's especially for the underage developers who donot have a GitHub account.
