import requests,time,os,math
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.image import AsyncImage
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.core.window import Window
from kivy.properties import StringProperty
import asynckivy as ak

class ImageButton(ButtonBehavior, AsyncImage):
    pass 

class ErrorPopup(Popup):
    error_text = StringProperty('')
    def __init__(self, error_text, **kwargs):
        super().__init__(**kwargs)
        self.error_text = error_text

class MainWindow(Widget):
    size_refrence = {"Small":{"name":"small","size":(146,204)},"Medium":{"name":"normal","size":(300,400)},"Large":{"name":"normal","size":(488,680)},"Ex-Large":{"name":"large","size":(672,936)}}    
    card_size = "Medium"
    col_width = size_refrence[card_size]["size"][0]
    page = 1
    page_size = 50
    current_search = ""
    
    def size_click(self,spinner):
        self.ids.results_grid.clear_widgets()
        self.card_size = spinner
        self.col_width = self.size_refrence[spinner]["size"][0]
        self.ids.results_grid.cols = (Window.width//self.size_refrence[spinner]["size"][0])
        self.display_results()

    async def display_results(self,selected_page):
        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        for card in selected_page:
            ak.sleep(.1)
            try:
                source = card["image_uris"][self.size_refrence[self.card_size]["name"]]
                results_grid.add_widget(ImageButton(source=source,size_hint=(None,None),size=self.size_refrence[self.card_size]["size"], on_press=self.press))
            except:
                source = card["card_faces"][0]["image_uris"][self.size_refrence[self.card_size]["name"]]
                results_grid.add_widget(ImageButton(source=source,size_hint=(None,None),size=self.size_refrence[self.card_size]["size"],on_press=self.press))

    def get_api_pages(self):
        first_page = ((self.page-1)//175)+1
        last_page = (((self.page*self.page_size)-1)//175)+1
        return range(first_page,last_page+1)
    
    def click_page(self,instance):
        self.page = int(instance.text)
        api_pages = self.get_api_pages()
        card_list = []
        last_card = self.page*self.page_size
        first_card = last_card-(self.page_size-1)
        for page in api_pages:
            request = requests.get("https://api.scryfall.com/cards/search",{"q":self.current_search,"page":page})
            cards = request.json()
            for card in cards["data"]:
                card_list.append(card)
            last_api_page = 175*page
        


    def create_pages(self,l,n=50): 
        return {int(i + 1): l[i:i + n] for i in range(0, len(l), n)}

    def create_page_select(self,num_results):
        page_options = self.ids.page_options
        page_options.clear_widgets()
        max_page = int(math.ceil(num_results/self.page_size))
        page_options.cols = max_page
        for page in range(max_page):
            page_button = Button(text=str(page+1),size_hint=(None,None),size=(30,20))
            page_button.bind(on_press=self.click_page)
            page_options.add_widget(page_button)         

    def random_search(self):
        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        search_text = self.ids.search_bar.text
        request = requests.get("https://api.scryfall.com/cards/random",{"q":search_text})
        card = request.json()
        if request.ok:
            try:
                source = card["image_uris"][self.size_refrence[self.card_size]["name"]]
                results_grid.add_widget(ImageButton(source=source,size_hint=(None,None),size=self.size_refrence[self.card_size]["size"], on_press=self.press))
            except:
                source = card["card_faces"][0]["image_uris"][self.size_refrence[self.card_size]["name"]]
                results_grid.add_widget(ImageButton(source=source,size_hint=(None,None),size=self.size_refrence[self.card_size]["size"],on_press=self.press))
        else:
            error_message = request.json()
            error_pop = ErrorPopup(str(request.reason)+":\n"+str(error_message["warnings"]))
            error_pop.open()

    def search(self):
        card_list = []
        self.current_search = self.ids.search_bar.text
        if self.current_search != "":
            request = requests.get("https://api.scryfall.com/cards/search",{"q":self.current_search})
            if request.ok:
                cards = request.json()
                for card in cards["data"]:
                    card_list.append(card)

                if len(cards["data"]) > self.page_size:
                    #Handles when search has multiple pages of results on the Scryfall API
                    if cards["has_more"] == True:
                        selected_page = card_list[:self.page_size]     
                    #Handles when search only has 1 page of results in the scryfall API
                    else:
                        selected_page = self.create_pages(card_list)
                #Handles when search only has 50 or less cards
                else:
                    selected_page = card_list
                    
                self.page = 1
                ak.start(self.display_results(selected_page))
                self.create_page_select(cards["total_cards"])

            else:
                error_message = request.json()
                error_pop = ErrorPopup(str(request.reason)+":\n"+str(error_message["warnings"]))
                error_pop.open()
        else:
            error_pop = ErrorPopup("Search cannot be blank.")
            error_pop.open()
                        
    def press(self,instance):
        results_grid = self.ids.results_grid
        results_grid.clear_widgets()
        results_grid.add_widget(ImageButton(source=instance.source,size_hint=(None,None),size=instance.size))

class ScryApp(App):
    def build(self):
        return MainWindow()
    
if __name__ == "__main__":
    ScryApp().run()