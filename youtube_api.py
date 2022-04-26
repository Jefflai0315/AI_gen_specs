from googleapiclient.discovery import build
import pickle
import os
import pandas as pd
from google_key import * 

class ScrapingApi: 
    def __init__(self, key): 
        self.key = key

class Youtube_api(ScrapingApi): 
    def __init__(self, key): 
        super().__init__(key)
        self.youtube = build('youtube', 'v3', developerKey=key)
    
    def search(self, search_terms, max_result=45):        
        vid_id = []             	# video id
        vid_page = []       		# video links (https...)
        vid_title = []              # video title
        num_comments = []           # official number of comments
        load_error = 0              # error counter
        can_load_title = []         # temp. list for storing title w/o loading error
        can_load_page = []          # temp. list for storing links w/o loading error
        num_page = []               # comment_response page number
        page_title = []             # comment_response video title
        comment_resp = []           # comment_response
        comment_list = []           # temp. list for storing comments
        comment_data = []           # comments & replies from comment_response
        all_count = 0               # total number of comments  
        
        request = self.youtube.search().list(
            q=search_terms,
            maxResults=max_result,
            part="id",
            type="video"
        )

        search_response = request.execute()
        for i in range(max_result):
            videoId = search_response['items'][i]['id']['videoId']
            vid_id.append(videoId)
            vid_page.append("https://www.youtube.com/watch?v=" + videoId)

        for id in vid_id: 
            request = self.youtube.videos().list(
                part="snippet, statistics",
                id=id
            )
            video_response = request.execute()
            title = video_response['items'][0]['snippet']['title']
            vid_title.append(title)
            
            try:
                comment_count = video_response['items'][0]['statistics']['commentCount']
                num_comments.append(comment_count)
            except:
                # comments are turned off 
                num_comments.append(0)

        '''get comment data'''
        # print("Get comment data...")
        for i in range(len(vid_id)):
            try:        # in case loading error
                request = self.youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=vid_id[i]
                    )
                comment_response = request.execute()
                comment_resp.append(comment_response)   # append 1 page of comment_response
                pages = 1
                num_page.append(pages)                  # append page number of comment_response
                page_title.append(vid_title[i])         # append video title along with the comment_response

                can_load_page.append(vid_page[i])       # drop link if it can't load (have at least 1 comment page)
                can_load_title.append(vid_title[i])     # drop title if it can't load (have at least 1 comment page)

                test = comment_response.get('nextPageToken', 'nil')     # check for nextPageToken
                while test != 'nil':                                    # keep running until last comment page
                    next_page_ = comment_response.get('nextPageToken')
                    request = self.youtube.commentThreads().list(
                        part="snippet,replies",
                        pageToken=next_page_,
                        videoId=vid_id[i]
                        )
                    comment_response = request.execute()
                    # print(comment_response)

                    comment_resp.append(comment_response)   # append next page of comment_response
                    pages += 1
                    num_page.append(pages)              # append page number of comment_response
                    page_title.append(vid_title[i])     # append video title along with the comment_response

                    test = comment_response.get('nextPageToken', 'nil')     # check for nextPageToken (while loop)
            except:
                load_error += 1

            # Copy & Paste

        print("Videos that can load...")
        vid_page = can_load_page                    # update vid_page with those with no load error
        vid_title = can_load_title                  # update vid_title with those with no load error
        for i in range(len(vid_title)):
            if vid_title[i] == 'YouTube':           # default error title is 'YouTube'
                vid_title[i] = 'Video_' + str(i+1)  # replace 'YouTube' with Video_1 format
            print(i + 1, vid_title[i])
        # Copy & Paste


        '''sift comments into structure'''
        print("Get individual comment...")
        print(len(comment_resp))
        for k in range(len(comment_resp)):
            count = 0                                                     # comment counter
            comments_found = comment_resp[k]['pageInfo']['totalResults']  # comments on 1 comment_response page
            count = count + comments_found
            print(count)
            for i in range(comments_found):
                try:
                    print("\n comments found \n")
                    comment_list.append(comment_resp[k]['items'][i]['snippet']['topLevelComment']['snippet']['textDisplay'])

                    reply_found = comment_resp[k]['items'][i]['snippet']['totalReplyCount']    # for comment 'i'
                    count = count + min(reply_found, 5)     # YT provides max of 5 replies per comment
                    for j in range(min(reply_found, 5)):
                        try:
                            comment_list.append(comment_resp[k]['items'][i]['replies']['comments'][j]['snippet']['textDisplay'])
                            print(comment_resp[k]['items'][i]['replies']['comments'][j]['snippet']['textDisplay'])
                            print(j+1, 'out of', reply_found, 'replies captured')
                        except:
                            print("missing reply")
                except:
                    print("missing comment")            # or too many comments (e.g. 7.3K comments)
            # Copy & Paste (optional)

            comment_data.append(comment_list.copy())    # all comments on 1 comment_response page, use .copy()
            comment_list.clear()
            all_count += count

        combined_data = list(zip(page_title, num_page, comment_data))
        pickle.dump(combined_data, open("support/%s/combined_data.pkl" % search_terms, "wb"))

        '''print summary'''
        combined_data = pd.read_pickle("support/%s/combined_data.pkl" % search_terms)   # open as df
        pd.set_option('colwidth', 30)
        df = pd.DataFrame(combined_data, columns=['Title', 'Page', 'Comments'])
        return df


if __name__ == "__main__": 
    youtube_api = Youtube_api(key)
    df = youtube_api.search("heater_product")
    # print(df.describe())









