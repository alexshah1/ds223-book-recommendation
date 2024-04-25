# Recommendation Model

## How Does It Work?

Our recommendation model works by generating embeddings for the books and then calculating the cosine similarity between the embeddings of the input book and all other books. The books with the highest cosine similarity are recommended.


## Additional Filtering

Additional filters can be applied to ensure the model works faster. One such filter is the availability of the book. If the book is not available, it will not be recommended. This filter can be turned off if you want to recommend books irrespective of their availability.

## Current Functionality

As of now, the package has the following functionality in terms of recommendations:

::: kitab.recommendation_model.models