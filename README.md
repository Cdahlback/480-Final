# 480-Final

## Introduction 

- The Great CS Project  

- The scope? 

## Microservices Chosen 

#### Three microservice  

- User Authentication/LogIn 

- POST  

- GET  

## Packaging 

## Compose Stack 

 

..How you'll pass data between services when nec... 

The User Authentication Service handles user login and access.  

Users upload files via file postings.  

Users view uploaded files via getting list 

  

The microservices should be Web applications - typically backend Web APIs. 

At least one of your microservices should involve storing data in block storage via S3. This can be as simple as "receive files from a user and provide a list of those files".  

As part of this process, start to think about the API each of your microservices will expose - both to external consumers of the API as well as "inter-service" communication amongst the microservices. Think about how you'll pass data between services when necessary - will you require explicit restricted API calls, will you simply depend on a database or file store, or will you use a hybrid approach? Document this in your "mini-RAD". 
