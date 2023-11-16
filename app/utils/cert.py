import os
from PyPDF2 import PdfWriter, PdfReader
from PIL import Image, ImageFont, ImageDraw

class Certificate:
    def __init__(self, config):
        self.template = config['template']
        self.font_detail = config['font']
        self.p_box = tuple(config['participantBox'])
        self.e_box = tuple(config['eventBox'])
        self.title = config['title']
        self.author = config['author']

        self.blank_certificate = Image.open(self.template)
        self.font = ImageFont.truetype(self.font_detail['name'], self.font_detail['size'])

    def create(self, name, event, filename):
        image = self.blank_certificate.copy()

        draw = ImageDraw.Draw(image)

        name_box = self.font.getbbox(name)
        event_box = self.font.getbbox(event)

        name_x = self.p_box[0] + ((self.p_box[2] - self.p_box[0]) // 2) - ((name_box[2] - name_box[0])//2)
        event_x = self.e_box[0] + (((self.e_box[2] - self.e_box[0]) // 2) - ((event_box[2] - event_box[0])//2))

        name_coords = (name_x, self.p_box[1])
        event_coords = (event_x, self.e_box[1])

        draw.text(name_coords, name, font=self.font, fill=(0,0,0))
        draw.text(event_coords, event, font=self.font, fill=(0,0,0))
        # image.save(f"{filename}.jpg", resolution=100.00)
        image.save(f"{filename}.pdf", format="PDF", resolution=100.00)
        self.attach_metadata(filename)

    def attach_metadata(self, filename):
        reader = PdfReader(f"{filename}.pdf")
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        writer.add_metadata({
            "/Title": self.title,
            "/Author": self.author,
        })

        with open(f"{filename}.pdf", "wb") as f:
            writer.write(f)

    @staticmethod
    def check_config(config):
        """
        Returns int value.

        1: Config Keys not found.
        2: Font Keys not found.
        3: Template File not found.
        5: Font File not found.
        0: Required items are available.
        """
        keys = ['template', 'font', 'participantBox', 'eventBox', 'title', 'author']
        for key in keys:
            if key not in config.keys():
                return 1

        fontkeys = ['name', 'size']
        for key in fontkeys:
            if key not in config['font'].keys():
                return 2

        path = os.path.abspath(os.path.dirname(__name__))

        template = os.path.join(path, config['template'])
        font = os.path.join(path, config['font']['name'])

        if not os.path.exists(template):
            return 3

        if not os.path.exists(font):
            return 5

        return 0
