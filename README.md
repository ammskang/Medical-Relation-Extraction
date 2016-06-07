AUTHORS: Rahul Verma and Spiro Razis

This is an NLP project for medical relcation extraction.


The 80_20_split.py sperates our data files, beneficial.txt and harmful.txt,  into 80% training data and 20% test data.

The other programs in this project train on the training data (where we pull our features from the training data) and use logistic regression and SVMs to make predictions on the test data. Also, at the end these programs output the accuracy of our model.

entitiesbased.py pulls out the features of just the "entites" from our training data during training.

entitiesmiddle.py pulls out the features of just the "entites" and the words between the entities in our training data during training.

unibaised.py pulls out all word in our training data but it removes words that are in common between the beneficial.txt and harmful.txt files.

HOW TO USE (IN COMMAND LINE):

	first create the 80-20 split by:
		python3 80 20 split.py beneficial.txt harmful.txt
	
	next depending on what features you want to train on use any of the following:
		python3 entitiesbased.py beneficial_80_20_Split.txt harmful_80_20_Split.txt

		python3 entitiesmiddle.py beneficial_80_20_Split.txt harmful_80_20_Split.txt

		python3 unibaised.py beneficial_80_20_Split.txt harmful_80_20_Split.txt
