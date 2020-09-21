import main2
import pandas as pd


def suggest_restaurant(foodtype, area, pricerange):
    
    
    df = pd.read_csv("restaurant_info.csv")
    subframe = df[(df["food"] == foodtype) & (df["area"] == area) & (df["pricerange"] == pricerange)]
    
   
    
    restaurant = subframe[:1]
    
    if len(subframe) == 0:
        print("Sorry no restaurant with your preferences") 
    
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
    
    if dialog_act == "inform":
        
        if text == "any":
            
            if topic == "foodtype":
                foodtype = "any"
                
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
                
            if topic == "area":
                area = "any"
                
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
            
            if topic == "pricerange":
                pricerange = "any"
                
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
        
        if area == "" and (('part of town' in text) or ("center" in split) or ("north" in split) or ("east" in split) or ("south" in split) or ("west" in split)):
              
             
              
              if "part of town" in split:
                  area = split[(split.index('part')) - 1]         
                  
                  if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                  elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                  else:
                     return suggest_restaurant(foodtype, area, pricerange)
                 
              if "center" in split:
                   area = "center"
                   
                   if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                   elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                   else:
                     return suggest_restaurant(foodtype, area, pricerange)
                 
              if "north" in split:
                   area = "north"
                   
                   if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                   elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                   else:
                     return suggest_restaurant(foodtype, area, pricerange)
                 
              if "east" in split:
                   area = "east"
                   
                   if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                   elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                   else:
                     return suggest_restaurant(foodtype, area, pricerange)
                 
              if "south" in split:
                   area = "south"
                   
                   if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                   elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                   else:
                     return suggest_restaurant(foodtype, area, pricerange)
              
              if "west" in split:
                   area = "center"
                   
                   if pricerange == "":
                     print("What price range would you like?")
                     topic = "pricerange"
                     return foodtype, area, pricerange
                   elif foodtype == "":
                     print("What type of food would you like")
                     topic = "foodtype"
                     return foodtype, area, pricerange
                   else:
                     return suggest_restaurant(foodtype, area, pricerange)         
                
        if pricerange == "" and any(word in ["moderate", "cheap", "expensive"] for word in split):
            
           
            
            if "moderate" in split:
                pricerange = "moderate"
                
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
             
            elif "cheap" in split:
                pricerange = "cheap"
                
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "food"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
                
            elif "expensive" in split:
                pricerange = "expensive"
                
                
                if area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                elif foodtype == "":
                    print("What type of food would you like")
                    topic = "foodtype"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
        
        if foodtype == "" and 'food' in split:
                
                foodtype = split[(split.index('food')) - 1]         
                
                if pricerange == "":
                    print("What price range would you like?")
                    topic = "pricerange"
                    return foodtype, area, pricerange
                elif area == "":
                    print("In what area would you like to look for a restaurant?")
                    topic = "area"
                    return foodtype, area, pricerange
                else:
                    return suggest_restaurant(foodtype, area, pricerange)
              

        if foodtype != "" and area != "" and pricerange != "":
                return suggest_restaurant(foodtype, area, pricerange)
            
        return("The system did not understand the input, please clarify.")
       


if __name__ == '__main__':

    
    df = main2.read_file()
    train_df, test_df = main2.generate_dataframe(df)

    x_train = train_df['text'].values
    x_test = test_df['text'].values
    y_test = test_df['label'].values
    y_train = train_df['label'].values   
    
    classifier, vectorizer = main2.logistic_regression(x_train, x_test, y_test, y_train)
    
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
          
            

      
        
    

        
    print("Goodbye, enjoy your meal!")