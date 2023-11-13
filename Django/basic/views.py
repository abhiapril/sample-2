from django.shortcuts import redirect, render
from django.contrib import messages

# from .models import Reccdb
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import google.generativeai as palm
import pandas as pd
from .models import Reccdb

API_KEY='AIzaSyAsU_bYnO8j_aTCgOvT7H8Pfiq6DPvd6x8'


def Homepage(request):

    if request.method == "POST":
        country_arr = [0,0,0,0,0,0]
        purpose_arr = [0,0]
        adults_arr = [0,0,0]

        
        try :
            country = request.POST.get('country')
            print(country,"anzk")
            if country == 'uk':
                country_arr[0] = 1
            elif country == 'spain':
                country_arr[1] = 1
            elif country == 'france':
                country_arr[2] = 1
            elif country == "netherlands":
                country_arr[3] = 1
            elif country == "austria":
                country_arr[4] = 1
            elif country == "italy":
                country_arr[5] = 1
           
        except :
            messages.error(request, 'Fields cant be blank')
            return redirect('homepage')
        
        try :
            purpose = request.POST.get('purpose')
            if purpose == 'business':
                purpose_arr[0] = 1
            elif purpose == 'leisure':
                purpose_arr[1] = 1
            
        except : 
            messages.error(request, "Feld cant be empty")
            return redirect('homepage')

        
        try:
            adults = request.POST.get('adults')
            if adults == 'solo':
                adults_arr[0] = 1
            elif adults == 'couple':
                adults_arr[1] = 1
            elif adults == 'group':
                adults_arr[2] = 1

        except:
            messages.error(request, "Feld cant be empty")
            return redirect('homepage')
        
        arr = country_arr + purpose_arr + adults_arr

        df=pd.read_csv("./saved_models/clean_data.csv")

        df = df.drop(['review_date', 'lat', 'lng', 'total_number_of_reviews_reviewer_has_given', 'positive_review',
                'negative_review','All_Review','reviewer_nationality'], axis=1)
        
        hotelLeisureCounts = df[df['tags'].str.contains('Leisure')].groupby('hotel_name')['hotel_name'].count().sort_values(ascending=False)
        print("Leisure Counts: ", len(hotelLeisureCounts))
        #print(hotelLeisureCounts)

        hotelBusinessCounts = df[df['tags'].str.contains('Business')].groupby('hotel_name')['hotel_name'].count().sort_values(ascending=False)
        print("Business Counts: ", len(hotelBusinessCounts))
        #print(hotelBusinessCounts)

        hotelSoloCounts = df[df['tags'].str.contains('Solo')].groupby('hotel_name')['hotel_name'].count().sort_values(ascending=False)
        print("Solo Traveller Counts: ", len(hotelSoloCounts))

        hotelCoupleCounts = df[df['tags'].str.contains('Couple')].groupby('hotel_name')['hotel_name'].count().sort_values(ascending=False)
        print("Couple Counts: ", len(hotelCoupleCounts))

        hotelGroupCounts = df[df['tags'].str.contains('Group')].groupby('hotel_name')['hotel_name'].count().sort_values(ascending=False)
        print("Group Counts: ", len(hotelGroupCounts))

        uniqueHotels=df['hotel_name'].unique().tolist()

        processedDF=pd.DataFrame(index=df['hotel_name'].unique().tolist())
        processedDF['United Kingdom']=0;
        processedDF['Spain']=0;
        processedDF['France']=0;
        processedDF['Netherlands']=0;
        processedDF['Austria']=0;
        processedDF['Italy']=0;
        processedDF['Business']=0;
        processedDF['Leisure']=0;
        processedDF['Solo']=0;
        processedDF['Couple']=0;
        processedDF['Group']=0;

        uniqueHotels = df['hotel_name'].unique().tolist()

        for hotel in uniqueHotels:
            #Get country of the current hotel from df
            country = df[df['hotel_name'] == hotel]['country'].values[0]

            #Set the corresponding country column to 1 in processedDF
            processedDF.at[hotel, country] = 1

        print(processedDF.head,"anzuk")

        for hotel in uniqueHotels:
            #Update Trip type columns
            if hotel in hotelBusinessCounts and hotel in hotelLeisureCounts:
                if hotelLeisureCounts[hotel] > hotelBusinessCounts[hotel]:
                    processedDF.at[hotel, 'Leisure'] = 1
                elif hotelLeisureCounts[hotel] < hotelBusinessCounts[hotel]:
                    processedDF.at[hotel, 'Business'] = 1
                else:
                    processedDF.at[hotel, 'Leisure'] = 1
                    processedDF.at[hotel, 'Business'] = 1
            elif hotel in hotelBusinessCounts and hotel not in hotelLeisureCounts:
                processedDF.at[hotel, 'Business'] = 1
            elif hotel in hotelLeisureCounts and hotel not in hotelBusinessCounts:
                #print ("no business tag reviews for: ",hotel)
                processedDF.at[hotel, 'Leisure'] = 1
                
            #Update Traveller type columns
            #print hotelCoupleCounts['Best Western Amiral Hotel']
            if hotel in hotelSoloCounts and hotel in hotelCoupleCounts and hotel in hotelGroupCounts:
                soloCount=hotelSoloCounts[hotel]
                coupleCount=hotelCoupleCounts[hotel]
                groupCount=hotelGroupCounts[hotel]

                if soloCount>coupleCount and soloCount>groupCount:
                    processedDF.at[hotel, 'Solo'] = 1
                elif coupleCount>soloCount and coupleCount>groupCount:
                    processedDF.at[hotel, 'Couple'] = 1
                elif groupCount>soloCount and groupCount>coupleCount:
                    processedDF.at[hotel, 'Group'] = 1
                elif soloCount==coupleCount and soloCount>groupCount:
                    processedDF.at[hotel, 'Solo'] = 1
                    processedDF.at[hotel, 'Couple'] = 1
                elif soloCount==groupCount and soloCount>coupleCount:
                    processedDF.at[hotel, 'Solo'] = 1
                    processedDF.at[hotel, 'Group'] = 1
                elif coupleCount==groupCount and coupleCount>soloCount:
                    processedDF.at[hotel, 'Couple'] = 1
                    processedDF.at[hotel, 'Group'] = 1
                else:
                    processedDF.at[hotel, 'Solo'] = 1
                    processedDF.at[hotel, 'Couple'] = 1
                    processedDF.at[hotel, 'Group'] = 1


    

        userDF= pd.DataFrame(index=['user'],columns=['United Kingdom','Spain','France','Netherlands','Austria','Italy',
                                                'Business','Leisure',
                                                'Solo','Couple','Group'])
        userDF.loc['user'] = arr

        similarityDF=cosine_similarity(processedDF,userDF)
        #len(similarity.tolist())
        #similarity.tolist()
        similarityDF = pd.DataFrame(similarityDF)
        #Update similarity dataframe to add the average score column
        similarityDF['Average_Score']=0.0;

        for index, row in similarityDF.iterrows():
            #Get the hotel row from original dataframe
            hotelRow= df.loc[df['hotel_name'] == processedDF.index[index]].head(1)
            #Update score column
            similarityDF.at[index, 'Average_Score'] = hotelRow['average_Score_hotel']
        #print similarityDF
        #Sort similarityDF by cosine similarity score and then hotel average score
        similarityDF=similarityDF.sort_values(by=[0,'Average_Score'],ascending=False).head(5)
        recc_hotels=[]
        for index, row in similarityDF.iterrows():
            print("Hotel Name: ", processedDF.index[index])
            hotelRow = df.loc[df['hotel_name'] == processedDF.index[index]].head(1)
            #print("Average Score: ", hotelRow['average_Score_hotel'])
            print(processedDF.iloc[index])
            recc_hotels.append(processedDF.index[index])
            print('Similarity score', row[0])
            print('\n')

        palm.configure(api_key=API_KEY)
        model_list=[_ for  _ in palm.list_models()]
        for model in model_list:
            print(model.name)
        model_id='models/text-bison-001'
        df_new=pd.read_csv("./saved_models/clean_data.csv")
        text=df_new['positive_review'].head()
        promt='''
        Given some reviews of hotels. Give a short summary of the review between 50-60 words in a single paragraph. This will be used to give description for the hotel.
        '''
        hotels={}
        promt='''I will give you some reviews of a hotel. Study the review and give a summary of these reviews in 100 words. This is used to give a description about the hotel'''

        for recchotels in recc_hotels:
            temp_df=df_new[df_new['hotel_name']==recchotels]
            text=temp_df['positive_review'].head(25)
            completion = palm.generate_text(
                model=model_id,
                prompt=f"{text}\n{promt}",
                temperature=0.0,
                max_output_tokens=1600,
                candidate_count=1)
            hotels[recchotels]=completion.result
        print(hotels,"anzil")

        context = {
            'hotels' : hotels
        }

        return render(request, 'recommendations.html', context)
        
    
    return render(request, "index.html")




def About(request):
    return render(request, 'about.html')


def ContactUs(request):
    return render(request, 'contact.html')





def Recommend_hotels(request):

    return render(request, 'recommendations.html')
