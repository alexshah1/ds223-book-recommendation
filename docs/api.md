::: kitab.api.app
# Endpoints and Final Model Outputs 
## Retrieve Book Information:
-**Endpoint**: /book/{ISBN}
-Method: GET
-Output: JSON object containing book information (title, description, authors, genres)

 ## Add Book:
-**Endpoint**: /book
-Method: POST
-Input: JSON object containing book information (title, description, authors, genres)
-Output: Success or failure message

## Update Book:
-**Endpoint**: /book/{ISBN}
-Method: PUT
-Input: JSON object containing updated book information (title, description, authors, genres)
-Output: Success or failure message

## Get Authors by ISBNs:
-**Endpoint**: /authors
-Method: POST
-Input: List of ISBNs
-Output: JSON object containing authors for each ISBN

## Get Genres by ISBNs:
-**Endpoint**: /genres
-Method: POST
-Input: List of ISBNs
-Output: JSON object containing genres for each ISBN

## Retrieve Book History by Recommendation ISBN:
-**Endpoint**: /history/{recommendation_ISBN}
-Method: GET
-Output: JSON object containing history of recommendations for the book

## Add Recommendation Log:
-**Endpoint**: /history
-Method: POST
-Input: JSON object containing recommendation information (description, recommendation_ISBN, successful)
-Output: Success or failure message