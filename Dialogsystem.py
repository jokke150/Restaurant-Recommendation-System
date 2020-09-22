import main
import pandas as pd



cuisines = ["spanish", "italian", "french", "world", "thai", "bistro", "chinese", \
            "international", "portuguese", "mediterranean", "british", "indian",  \
            "gastropub", "turkish", "persian", "jamaican", "japanese", "seafood", \
            "cuban", "european", "lebanese", "creative" ]
    
locations = ["center", "north", "east", "south", "west"]

ranges = ["moderate", "cheap", "expensive"]



def suggest_restaurant(foodtype, area, pricerange):
    
    
    df = pd.read_csv("restaurant_info.csv")
    
    if not "any" in [foodtype, area, pricerange]:        
        subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]
        restaurant = subframe[:1]
    elif foodtype == "any" and not area == "any" and not pricerange == "any":
        subframe = df[(df["food"].isin(cuisines)) & (df["area"] == area) & (df["pricerange"] == pricerange)]
        restaurant = subframe[:1]
    elif not foodtype == "any"  and area == "any" and not pricerange == "any":
        subframe = df[(df["food"] == foodtype) & (df["area"].isin(locations)) & (df["pricerange"] == pricerange)]
        restaurant = subframe[:1]
    elif not foodtype == "any" and not area == "any" and pricerange == "any":
        subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"].isin(ranges))]
        restaurant = subframe[:1]
    elif foodtype == "any" and area == "any" and not pricerange == "any":
        subframe = df[(df["food"].isin(cuisines)) & (df["area"].isin(locations)) & (df["pricerange"] == pricerange)]
        restaurant = subframe[:1]
    elif not foodtype == "any" and area == "any" and pricerange == "any":
        subframe = df[(df["food"] == foodtype) & (df["area"].isin(locations)) & (df["pricerange"].isin(ranges))]
        restaurant = subframe[:1]
    elif foodtype == "any" and not area == "any" and pricerange == "any":
        subframe = df[(df["food"].isin(cuisines)) & (df["area"] == area) & (df["pricerange"].isin(ranges))]
        restaurant = subframe[:1]
    else:
        restaurant = df[:1]
    
    
    
        
      
    if len(subframe) == 0:
        if len(df[(df["food"] == foodtype) & (df["area"] == area)]) != 0:
        
            restaurant = df[(df["food"] == foodtype) & (df["area"] == area)][:1]
            name = restaurant["restaurantname"].iloc[0]
            foodtype = restaurant["food"].iloc[0]
            area = restaurant["area"].iloc[0]
            pricerange = restaurant["pricerange"].iloc[0]
            return print("No restaurant available in that pricerange. However,  " + name + " also has " +foodtype+ " food, is also in the " +area+ " part of town, but is in the " +pricerange+ " pricerange.")
    
        
        
    
    name = restaurant["restaurantname"].iloc[0]
    foodtype = restaurant["food"].iloc[0]
    area = restaurant["area"].iloc[0]
    pricerange = restaurant["pricerange"].iloc[0]
    
    
    return print(str(name) + " is a nice restaurant in the " + str(area) + " part of town that serves " + str(foodtype) + " food in the " + str(pricerange) + " price range")

def input_output_match(text, dialog_act, foodtype, area, pricerange, topic):
    
    split = text.split()
    
    if dialog_act == "affirm":
        if foodtype == "":
            return print("What type of food would you like")
        if area == "":
            return print("In what area would you like to look for a restaurant?")
        if pricerange == "":
            return print("What price range would you like?")
       
    if dialog_act == "hello":
        return print("You can ask for restaurants by area, price range or food type")
    
    
    if dialog_act == "reqalts":
        
     
        #If foodtype was known but a new foodtype preference is expressed, save this new one
        if foodtype != "" and any(word in cuisines for word in split):
            for word in cuisines:
                if word in split:
                    foodtype = word 
                    return suggest_restaurant(foodtype, area, pricerange)
         
        #If foodtype area was known but a new area preference is expressed, save this new one
        if area != "" and any(word in locations for word in split):
            for word in locations:
                if word in split:
                    area = word 
                    return suggest_restaurant(foodtype, area, pricerange)
        
         
        #If pricerange was known but a new foodtype preference is expressed, save this new one
        if pricerange != "" and any(word in ranges for word in split):
            for word in ranges:
                if word in split:
                    pricerange = word 
                    return suggest_restaurant(foodtype, area, pricerange)
        
        
    
    
    
    if dialog_act == "inform":
        
        if text == "any":
            
            if topic == "foodtype":
                foodtype = "any"
                
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange, topic
                elif area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange, topic
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
                
            if topic == "area":
                area = "any"
                
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange, topic
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange, topic
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
            
            if topic == "pricerange":
                pricerange = "any"
                
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange, topic
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange, topic
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
                
                
        #Check if the area is unknown but mentioned by the user
        if area == "" and any(word in locations for word in split):
        
            for word in locations:
                if word in split:
                    area = word
                    if pricerange == "":
                        print("What price range would you like?")
                        topic = "pricerange"
                        return foodtype, area, pricerange, topic
                    elif foodtype == "":
                        print("What type of food would you like")
                        topic = "foodtype"
                        return foodtype, area, pricerange, topic
                    else:
                        return suggest_restaurant(foodtype, area, pricerange)
             
               
        #Check if the pricerange is unknown but mentioned by the user    
        if pricerange == "" and any(word in ranges for word in split):
            
            
          
            for word in ranges:
                if word in split:
                    pricerange = word
                    if area == "":
                        print("In what area would you like to look for a restaurant?")
                        topic = "area"
                        return foodtype, area, pricerange, topic
                    elif foodtype == "":
                        print("What type of food would you like")
                        topic = "foodtype"
                        return foodtype, area, pricerange, topic
                    else:
                        return suggest_restaurant(foodtype, area, pricerange)
             
            
        #Check if the foodtype is unknown but mentioned by the user
        if foodtype == "" and any(word in cuisines for word in split):
                
                for word in cuisines:
                    if word in split:
                        foodtype = word
                        if pricerange == "":
                            print("What price range would you like?")
                            topic = "pricerange"
                            return foodtype, area, pricerange, topic
                        elif area == "":
                            print("In what area would you like to look for a restaurant?")
                            topic = "area"
                            return foodtype, area, pricerange, topic
                        else:
                            return suggest_restaurant(foodtype, area, pricerange)
        
        
       
            
              

        if foodtype != "" and area != "" and pricerange != "":
                return suggest_restaurant(foodtype, area, pricerange)
            
        return("The system did not understand the input, please clarify.")
       


if __name__ == '__main__':

    
    df = main.read_file()
    train_df, test_df = main.generate_dataframe(df)

    x_train = train_df['text'].values
    x_test = test_df['text'].values
    y_test = test_df['label'].values
    y_train = train_df['label'].values   
    
    classifier, vectorizer = main.logistic_regression(x_train, x_test, y_test, y_train)
    
    varinp = 1
    
    dialog_act = ""
    foodtype= ""
    area = ""
    pricerange= ""
    topic = ""
    
    print("Hello, welcome to the restaurant service")
    
    
    while not (dialog_act == "thankyou" or dialog_act == "bye" ):
        
       
        varinp = input().lower()
        i = vectorizer.transform([varinp])
        dialog_act = classifier.predict(i)
        
        info = input_output_match(varinp, dialog_act, foodtype, area, pricerange, topic)
        
        if type(info) == tuple:
            foodtype = info[0]
            area = info[1]
            pricerange = info[2]
            topic = info[3]
          
         

      
        
    

        
    print("Goodbye, enjoy your meal!")
