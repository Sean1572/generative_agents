import os
import json

class SocialMedia():
    def __init__(self, storage):
        self.content_fs = f"{storage}/social_media.json"
        if os.path.exists(self.content_fs):
            with open(self.content_fs, "r") as file:
                self.content = json.load(file)
                self.content_count = len(list(self.content.keys()))
                print(self.content)
        else:
             self.content = {}
             self.content_count = 0
             self.save()

    def save(self):
        with open(self.content_fs, "w") as file:
            json.dump(self.content, file, indent=2)

    def get_content(self):
        ranking = [(id, content) for content in self.content]
        return sorted(ranking, key=0)[-5:]

    def write_post(self, persona, content, time):
        self.content[str(self.content_count)] = {
                "persona": persona,
                "content": content,
                "time": time,
                "comments": [],
                "likes": []
            }
        self.content_count += 1
        

    def write_comment(self, persona, post_id, comment, time):
        self.content[str(post_id)]["comments"].append({
            "persona": persona,
            "content": comment,
            "time": time,
        })

    def like_post(self, persona, post_id):
        self.content[str(post_id)]["likes"].append(persona)

    #def like_comment(persona, post_id):


if __name__ == '__main__':
    print("start")
    media = SocialMedia("../../environment/frontend_server/storage")
    media.write_post("test1", "Hello, this is my frist post!", 0)
    media.write_post("test2", "Hello, this is MY frist post!", 1)
    media.write_comment("test1", 1, "Hello, test2 i'm test1", 2)
    media.like_post("test2", 0)
    print(media.get_content())
    media.save()