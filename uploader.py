from datetime import datetime, timedelta

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium_firefox.firefox import Firefox


import time
from pathlib import Path

import logging

logging.basicConfig()

def main():

    current_working_dir = str(Path.cwd())
    driver = Firefox(current_working_dir, current_working_dir, 
        full_screen=False, 
        disable_images=True,
        #headless=True,
    )

    uploader = YouTubeUploader(driver, "up.mov", 
        thumbnail_path = "up.png", 
        title = "Test",
        metadata= {
            "description": "Test test\nNew Line :) X3  👴 ", 
            "playlists": ["Season 3", "R/Inceltears"],
            "category": "CREATOR_VIDEO_CATEGORY_ENTERTAINMENT",
            "product_placement": True,
            "release_date": datetime.now() + timedelta(minutes=567)
        })
    uploader.upload()


    #CREATOR_VIDEO_CATEGORY_FILM
    #CREATOR_VIDEO_CATEGORY_AUTOS
    #CREATOR_VIDEO_CATEGORY_MUSIC
    #CREATOR_VIDEO_CATEGORY_PETS
    #CREATOR_VIDEO_CATEGORY_SPORTS
    #CREATOR_VIDEO_CATEGORY_TRAVEL
    #CREATOR_VIDEO_CATEGORY_GADGETS
    #CREATOR_VIDEO_CATEGORY_PEOPLE
    #CREATOR_VIDEO_CATEGORY_COMEDY
    #CREATOR_VIDEO_CATEGORY_ENTERTAINMENT
    #CREATOR_VIDEO_CATEGORY_NEWS
    #CREATOR_VIDEO_CATEGORY_HOWTO
    #CREATOR_VIDEO_CATEGORY_EDUCATION
    #CREATOR_VIDEO_CATEGORY_SCIENCE
    #CREATOR_VIDEO_CATEGORY_GOVERNMENT






class YouTubeUploader:

    def __init__(self, browser, video_path, thumbnail_path = None, title = None, metadata = {"description":None, "tags":[]}):
        self.video_path = video_path
        self.thumbnail_path = thumbnail_path 
        self.title = title
        self.metadata = metadata

        self.browser = browser

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        
        self.__validate_inputs()

    def __validate_inputs(self):

        if not self.title:
            self.logger.warning("The video title was not found in a metadata file")
            self.title = Path(self.video_path).stem
            self.logger.warning("The video title was set to {}".format(Path(self.video_path).stem))
        if not self.metadata["description"]:
            self.logger.warning("The video description was not found in a metadata file")

    def upload(self):
        try:
            self.__login()
            return self.__upload()
        except Exception as e:
            print(e)
            self.__quit()
            raise


    def __login(self):
        self.browser.get("https://www.youtube.com")
        time.sleep(1)

        if self.browser.has_cookies_for_current_website():
            self.browser.load_cookies()
            time.sleep(1)
            self.browser.refresh()
        else:
            self.logger.info('Please sign in and then press enter')
            input()
            self.browser.get("https://www.youtube.com")
            time.sleep(1)
            self.browser.save_cookies()

    def __write_in_field(self, field, string, clear=False):
        write_action = ActionChains(self.browser.driver)

        write_action.move_to_element(field).perform()
        write_action.click(field).perform()
        
        if clear:
            field.clear()
            field.send_keys(Keys.CONTROL + "a")
            field.send_keys(Keys.DELETE)
        
        field.send_keys(string)
        time.sleep(.33)

    def __upload(self):
        self.browser.get("https://www.youtube.com")
        time.sleep(1)
        self.browser.get("https://www.youtube.com/upload")
        time.sleep(1)
        absolute_video_path = str(Path.cwd() / self.video_path)
        self.browser.driver.find_element_by_xpath("//input[@type='file']").send_keys(absolute_video_path)
        self.logger.debug('Attached video {}'.format(self.video_path))


        time.sleep(.33)

        self.__set_title_and_description()

        time.sleep(.33)
        
        if self.thumbnail_path is not None:
            self.__set_thumbnail()

        time.sleep(.33)
        
        if self.metadata["playlists"] not in (None, []):
            self.__set_playlists()

        time.sleep(.33)

        self.__set_kids()

        time.sleep(.33)

        self.__activate_advanced_options()

        time.sleep(.33)

        if self.metadata["release_date"] == True:
            self.__set_product_placement()

        time.sleep(.33)

        if self.metadata["category"] is not None:
            self.__set_category()

        time.sleep(.33)

        self.__next_page()
        
        self.__next_page()

        self.__next_page()
        
        time.sleep(.33)

        self.__set_scheduler()

        time.sleep(1)

        # get video ID

        video_id = self.browser.driver.find_element_by_xpath("//ytcp-uploads-dialog//ytcp-uploads-review//ytcp-video-info//span/a").text
        self.logger.debug(video_id)

        time.sleep(.33)
      
        #Finish upload
        done_button = self.browser.driver.find_element_by_id("done-button")

        # Catch such error as
        # "File is a duplicate of a video you have already uploaded"
        if done_button.get_attribute('aria-disabled') == 'true':
            error_message = self.browser.driver.find_element_by_xpath("//*[@id='error-message']").text
            self.logger.error(error_message)
            return False, None

        done_button.click()
        self.logger.debug("Settings done")

        time.sleep(10)

        #Check upload status
        progress_bar = self.browser.driver.find_element_by_xpath("//ytcp-uploads-still-processing-dialog//ytcp-video-upload-progress")
        
        upload_finished = False
        while not upload_finished:
            copytight_status = progress_bar.get_attribute("copyright-check-status")
            if copytight_status in ("STARTED", "COMPLETED"):
                upload_finished = True

            self.logger.debug(self.browser.driver.find_element_by_xpath("//ytcp-uploads-still-processing-dialog/ytcp-dialog//ytcp-video-upload-progress/span").text)
          
            time.sleep(2.5)
        
        self.browser.get(video_id)
        self.logger.debug("UPLOAD DONE")
        time.sleep(.33)

        self.__quit()
        return True, video_id


    def __next_page(self):
        action = ActionChains(self.browser.driver)
        next_button = self.browser.driver.find_element_by_id("next-button")
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", next_button)

        action.move_to_element(next_button)
        action.click(next_button).perform()

        self.logger.debug('Changed to next Page')

    ### DETAILS PAGE
    def __set_title_and_description(self):
        # Wait for uploadpage to load (get textfields)
        title_field = None
        for i in range(100):
            if title_field in (None, []):
                title_field = self.browser.driver.find_elements_by_id("textbox")
                print(title_field)
                time.sleep(1)
        
        
        # Set title
        self.__write_in_field(title_field[0], self.title, clear=True)
        self.logger.debug('The video title was set to \"{}\"'.format(self.title))

        time.sleep(.33)
        
        # Set description
        video_description = self.metadata["description"]
        if video_description:
            self.__write_in_field(title_field[1], video_description)
            self.logger.debug('The video description was set to \"{}\"'.format(self.metadata["description"]))

    def __set_thumbnail(self):
        # Set thumbnail
        absolute_thumbnail_path = str(Path.cwd() / self.thumbnail_path)
        self.browser.driver.find_element_by_xpath("//input[@id='file-loader']").send_keys(absolute_thumbnail_path)
        change_display = "document.getElementById('file-loader').style = 'display: block! important'"
        self.browser.driver.execute_script(change_display)
        self.logger.debug('Attached thumbnail {}'.format(self.thumbnail_path))

    def __set_playlists(self):
        action = ActionChains(self.browser.driver)

        #Playlist
        video_playlist_names = self.metadata["playlists"]
        
        playlist_area = self.browser.driver.find_element_by_xpath('//ytcp-video-metadata-playlists/ytcp-text-dropdown-trigger')
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", playlist_area)

        action.move_to_element(playlist_area)
        action.click(playlist_area).perform()

        time.sleep(.33)

        playlist_search = self.browser.driver.find_element_by_xpath("//ytcp-playlist-dialog//input")
        for playlist_name in video_playlist_names:
            try:
                self.__write_in_field(playlist_search, playlist_name, True)
            except:
                self.logger.warning('Unable to search playlists')

            sub_action = ActionChains(self.browser.driver)

            try:
                playlist_item = self.browser.driver.find_element_by_xpath("//ytcp-playlist-dialog//ytcp-checkbox-group//li//*[@id='checkbox-container']")
                sub_action.click(playlist_item).perform()
            
                self.logger.debug('Added to playlist {}'.format(playlist_name))
            except:
                self.logger.warning('Playlist "{}" does not exist'.format(playlist_name))

            
            
            time.sleep(.33)
        
        action2 = ActionChains(self.browser.driver)
        action2.send_keys(Keys.ESCAPE).perform()

    def __set_kids(self):
        # Kids Restrictions
        action = ActionChains(self.browser.driver)
        kids_element = self.browser.driver.find_element_by_id("made-for-kids-group").find_element_by_name("NOT_MADE_FOR_KIDS") #Change to MADE_FOR_KIDS if for kids
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", kids_element)

        action.move_to_element(kids_element).perform()
        action.click(kids_element).perform()
        
        self.logger.debug('Selected \"{}\"'.format("NOT_MADE_FOR_KIDS")) #Change to MADE_FOR_KIDS if for kids

    def __activate_advanced_options(self):
        # Advanced options
        action = ActionChains(self.browser.driver)
        more_options_element = self.browser.driver.find_element_by_xpath("//*[normalize-space(text()) = 'Mehr anzeigen']")
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", more_options_element)
        
        action.move_to_element(more_options_element).perform()
        action.click(more_options_element).perform()
        
        self.logger.debug('Clicked MORE OPTIONS')

    def __set_product_placement(self):
        # Product Placement
        action = ActionChains(self.browser.driver)
        more_options_element = self.browser.driver.find_element_by_xpath('//ytcp-video-metadata-editor-advanced/div[@class="paid-promotion"]//*[@id="checkbox-container"]')
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", more_options_element)
        
        action.move_to_element(more_options_element)
        action.click(more_options_element).perform()
       
        self.logger.debug('Set included ADs')

    def __set_category(self):
        action = ActionChains(self.browser.driver)
        category_trigger = self.browser.driver.find_element_by_xpath('//ytcp-video-metadata-editor-advanced/div[@id="category-container"]//ytcp-dropdown-trigger')
        self.browser.driver.execute_script("arguments[0].scrollIntoView()", category_trigger)
        
        action.move_to_element(category_trigger)
        action.click(category_trigger).perform()

        category_container = self.browser.driver.find_element_by_xpath('//ytcp-text-menu//*[@id="paper-list"]')
        category_items = category_container.find_elements_by_xpath('//tp-yt-paper-item')

        for category_item in category_items:
            category_name = category_item.get_attribute("test-id")

            if category_name == self.metadata["category"]:
                self.browser.driver.execute_script("arguments[0].scrollTop = arguments[1].offsetTop; ", category_container, category_item)

                sub_action = ActionChains(self.browser.driver)

                sub_action.move_to_element(category_item)
                sub_action.click(category_item).perform()
                
                time.sleep(.33)
       
        self.logger.debug('Set category to {}'.format(self.metadata["category"]))

    ### VISIBILITY
    def __set_scheduler(self):
        # Set upload time
        action = ActionChains(self.browser.driver)
        schedule_radio_button = self.browser.driver.find_element_by_id("schedule-radio-button")

        action.move_to_element(schedule_radio_button)
        action.click(schedule_radio_button).perform()
        self.logger.debug('Set delevery to {}'.format("schedule"))
        time.sleep(.33)

        #Set close action
        action_close = ActionChains(self.browser.driver)
        action_close.send_keys(Keys.ESCAPE)

        #date picker
        action_datepicker = ActionChains(self.browser.driver)
        datepicker_trigger = self.browser.driver.find_element_by_id("datepicker-trigger")

        action_datepicker.move_to_element(datepicker_trigger)
        action_datepicker.click(datepicker_trigger).perform()
        time.sleep(.33)

        date_string = self.metadata["release_date"].strftime("%d.%m.%Y")
        date_input = self.browser.driver.find_element_by_xpath('//ytcp-date-picker/tp-yt-paper-dialog//iron-input/input')

        self.__write_in_field(date_input, date_string, True)
        self.logger.debug('Set schedule date to {}'.format(date_string))

        action_close.perform()
        time.sleep(.33)


        #time picker
        action_timepicker = ActionChains(self.browser.driver)
        time_of_day_trigger = self.browser.driver.find_element_by_id("time-of-day-trigger")
        
        action_timepicker.move_to_element(time_of_day_trigger)
        action_timepicker.click(time_of_day_trigger).perform()
        time.sleep(.33)

        time_dto = (self.metadata["release_date"] - timedelta( 
                            minutes = self.metadata["release_date"].minute % 15,
                            seconds = self.metadata["release_date"].second,
                            microseconds = self.metadata["release_date"].microsecond))
        time_string = time_dto.strftime("%H:%M")
        
        time_container = self.browser.driver.find_element_by_xpath('//ytcp-time-of-day-picker//*[@id="dialog"]')
        time_item = self.browser.driver.find_element_by_xpath('//ytcp-time-of-day-picker//tp-yt-paper-item[text() = "{}"]'.format(time_string))
        
        self.logger.debug('Set schedule date to {}'.format(time_string))
        self.browser.driver.execute_script("arguments[0].scrollTop = arguments[1].offsetTop; ", time_container, time_item)

        time_item.click()

        action_close.perform()
        time.sleep(.33)



    ############ BLABLABLA ############

    def __get_video_id(self):
        video_id = None
        try:
            video_url_container = self.browser.driver.find_element_by_xpath("//span[@class='video-url-fadeable style-scope ytcp-video-info']")
            video_url_element = self.browser.driver.find_element_by_xpath("//a[@class='style-scope ytcp-video-info']",
                                                  element=video_url_container)
            video_id = video_url_element.get_attribute("href").split('/')[-1]
        except:
            self.logger.warning("Could not find video_id")
            pass
        return video_id

    def __quit(self):
        self.browser.quit()












if __name__ == "__main__":
    main()