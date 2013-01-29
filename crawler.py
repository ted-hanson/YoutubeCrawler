from gdata.youtube import service
from collections import defaultdict
from collections import Counter
import getpass
import re

#takes YoutubeService client and Youtube video id to grab comment stream using gdata api
def getCommentStream(client, vid):
    comment_feed = client.GetYouTubeVideoCommentFeed(video_id=vid)
    while comment_feed is not None:         #keep grabbing comments
        for comment in comment_feed.entry:
            yield comment
        try:
            comment_feed = client.GetYouTubeVideoCommentFeed(comment_feed.GetNextLink().href)
        except:
            comment_feed = None             #done grabbing comments because GetNextLink().href errored (null pointer)

#Calculates highest popularity based on replies/posts = popularity (downfall is no floating numbers in Counter()
def mostPopularAuthors(replies, posts): 
    mostPopular = {}
    
    for author, replies in replies.most_common(10): #only use the people with the most replies and then divide their replies by their posts
        mostPopular[author] = float(replies)/posts[author]
    listPopular = mostPopular.items()
    listPopular.sort(key=lambda x: -x[1])   #negative so that it sorts most first
    return listPopular
    
#Crawls through a Youbue video's comments
def crawlPage(vid):
    client = service.YouTubeService()       #creates YoutubeService object to query server
    
    #State variables to update
    replies = []
    authorRepliedTo = Counter()
    urlToAuthor = {}
    authorPosts = Counter()
    words = Counter()
    
    #Stream comments
    for comment in getCommentStream(client, vid):
        author = comment.author[0].name.text
        authorPosts[author] += 1    #Increment author posts
        for t in comment.link:
            if (t.rel == "self"):   #save self link so we can reference author later from comment href
                urlToAuthor[t.href] = author
            if (t.rel == "http://gdata.youtube.com/schemas/2007#in-reply-to"):
                replies.append((author, t.href))    #save reply url so we can use later as (replyAuthor, originalCommentLink)
        text = comment.content.text 
        validWords = re.compile("(\w[\w']*\w|\w)") 
        for word in validWords.findall(text):       #Continually increment Count object for each valid word
            words[word] += 1
            
    for reply in replies:   #go through the replies and increment which author got replied to
        authorRepliedTo[urlToAuthor[reply[1]]] += 1
    
    print "The most common words are:"
    print words.most_common(10)                                             #Most common words
    print "The most replied-to author was:"
    print authorRepliedTo.most_common(1)                                    #Author with the most replied to
    print "The most popular authors were:"
    print mostPopularAuthors(authorRepliedTo, authorPosts) #Authors with the highest popularity (replies per posts)

if __name__ == '__main__':
    crawlPage(raw_input("Please enter video id to crawl: ")) #could just enter video id manually here