import requests
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.image import AsyncImage
from kivy.uix.textinput import TextInput
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.animation import Animation
from kivy.uix.popup import Popup

# 📱 mobile window (simulation)
Window.size = (360, 640)

API_URL = "http://192.168.1.3:8000"


# =========================
# 🔐 LOGIN
# =========================
class LoginScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(15))

        self.username = TextInput(
            hint_text="Username",
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size='16sp'
        )

        self.password = TextInput(
            hint_text="Password",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(50),
            font_size='16sp'
        )

        # 🔥 UX: ENTER / TAB
        self.username.bind(on_text_validate=self.focus_password)
        self.password.bind(on_text_validate=self.login)

        self.msg = Label(text="", color=(1, 0, 0, 1))

        btn_login = Button(text="Login", size_hint_y=None, height=dp(50))
        btn_register = Button(text="Register", size_hint_y=None, height=dp(50))

        btn_login.bind(on_press=self.login)
        btn_register.bind(on_press=lambda x: setattr(self.manager, 'current', 'register'))

        layout.add_widget(Label(text="Login", font_size='22sp'))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.msg)
        layout.add_widget(btn_login)
        layout.add_widget(btn_register)

        self.add_widget(layout)

        # 🔥 autofocus na username
        self.username.focus = True

    # 🔥 TAB / ENTER → password
    def focus_password(self, instance):
        self.password.focus = True

    def login(self, instance):
        try:
            res = requests.post(f"{API_URL}/api/login/", json={
                "username": self.username.text.strip(),
                "password": self.password.text.strip()
            })

            data = res.json()

            if "user_id" in data:
                App.get_running_app().user_id = data["user_id"]
                self.manager.current = 'products'
            else:
                self.msg.text = "Invalid login"

        except:
            self.msg.text = "Server error"


# =========================
# 📝 REGISTER
# =========================
class RegisterScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(8))

        self.username = TextInput(hint_text="Username")
        self.password = TextInput(hint_text="Password", password=True)
        self.first_name = TextInput(hint_text="First name")
        self.last_name = TextInput(hint_text="Last name")
        self.email = TextInput(hint_text="Email")
        self.address = TextInput(hint_text="Address")

        self.msg = Label(text="")

        btn = Button(text="Register", size_hint_y=None, height=dp(50))
        back = Button(text="Back", size_hint_y=None, height=dp(50))

        btn.bind(on_press=self.register)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'login'))

        layout.add_widget(Label(text="Register", font_size='20sp'))
        layout.add_widget(self.username)
        layout.add_widget(self.password)
        layout.add_widget(self.first_name)
        layout.add_widget(self.last_name)
        layout.add_widget(self.email)
        layout.add_widget(self.address)
        layout.add_widget(self.msg)
        layout.add_widget(btn)
        layout.add_widget(back)

        self.add_widget(layout)

    def register(self, instance):
        try:
            res = requests.post(f"{API_URL}/api/register/", json={
                "username": self.username.text,
                "password": self.password.text,
                "first_name": self.first_name.text,
                "last_name": self.last_name.text,
                "email": self.email.text,
                "address": self.address.text
            })

            data = res.json()

            if "error" in data:
                self.msg.text = data["error"]
            else:
                self.msg.text = "Registered ✔"

        except:
            self.msg.text = "Server error"


# =========================
# 🛍️ PRODUCTS
# =========================
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, RoundedRectangle

class ProductScreen(Screen):
    def on_enter(self):
        self.selected_category = None
        self.build_ui()

    def build_ui(self):
        self.clear_widgets()

        main = BoxLayout(orientation='vertical')

        # 🎨 BIJELA POZADINA (VELIKI FIX)
        with self.canvas.before:
            Color(1, 1, 1, 1)
            self.bg = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(size=self.update_bg, pos=self.update_bg)

        # =========================
        # 📂 CATEGORY BAR
        # =========================
        cat_scroll = ScrollView(size_hint_y=None, height=dp(60))
        self.cat_layout = BoxLayout(size_hint_x=None, spacing=dp(10))
        self.cat_layout.bind(minimum_width=self.cat_layout.setter('width'))

        try:
            categories = requests.get(f"{API_URL}/api/categories/").json()

            # ALL
            btn = Button(text="All", size_hint=(None, 1), width=dp(100))
            btn.bind(on_press=lambda x: self.select_category(None, btn))
            self.cat_layout.add_widget(btn)

            for c in categories:
                btn = Button(text=c['name'], size_hint=(None, 1), width=dp(120))
                btn.bind(on_press=lambda x, cid=c['id'], b=btn: self.select_category(cid, b))
                self.cat_layout.add_widget(btn)

        except:
            self.cat_layout.add_widget(Label(text="Error"))

        cat_scroll.add_widget(self.cat_layout)

        # =========================
        # 🛍️ GRID
        # =========================
        self.scroll = ScrollView()

        self.grid = GridLayout(
            cols=2,
            spacing=dp(15),
            padding=dp(10),
            size_hint_y=None
        )
        self.grid.bind(minimum_height=self.grid.setter('height'))

        self.scroll.add_widget(self.grid)

        cart_btn = Button(text="🛒 Cart", size_hint_y=None, height=dp(55))
        cart_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'cart'))

        main.add_widget(cat_scroll)
        main.add_widget(self.scroll)
        main.add_widget(cart_btn)

        self.add_widget(main)

        self.load_products()

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    # =========================
    # CATEGORY SELECT
    # =========================
    def select_category(self, category_id, btn):
        self.selected_category = category_id

        # 🎨 highlight active
        for b in self.cat_layout.children:
            b.background_color = (1, 1, 1, 1)

        btn.background_color = (0.2, 0.6, 1, 1)

        self.load_products(category_id)

    # =========================
    # LOAD PRODUCTS
    # =========================
    def load_products(self, category_id=None):
        self.grid.clear_widgets()

        url = f"{API_URL}/api/products/"
        if category_id:
            url += f"?category_id={category_id}"

        products = requests.get(url).json()

        for p in products:
            card = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(260),
                padding=dp(10),
                spacing=dp(8)
            )

            # 🎨 CARD STYLE
            with card.canvas.before:
                Color(0.95, 0.95, 0.95, 1)
                card.bg = RoundedRectangle(radius=[15])

            def update_rect(instance, value):
                instance.bg.pos = instance.pos
                instance.bg.size = instance.size

            card.bind(pos=update_rect, size=update_rect)

            # 🖼️ IMAGE (VEĆA + CENTER)
            if p['image']:
                img = AsyncImage(
                    source=p['image'],
                    size_hint=(1, 0.6),
                    allow_stretch=True
                )
                card.add_widget(img)

            # 🏷️ NAME
            card.add_widget(Label(
                text=p['name'],
                font_size='14sp',
                color=(0, 0, 0, 1)
            ))

            # 💰 PRICE
            card.add_widget(Label(
                text=f"{p['price']}€",
                font_size='14sp',
                bold=True,
                color=(0.1, 0.5, 0.1, 1)
            ))

            # 🛒 BUTTON
            btn = Button(
                text="Add to Cart",
                size_hint_y=None,
                height=dp(45),
                background_color=(0.2, 0.6, 1, 1)
            )
            btn.bind(on_press=lambda x, prod=p: self.add(prod))

            card.add_widget(btn)

            self.grid.add_widget(card)

    def add(self, p):
        requests.post(f"{API_URL}/api/cart/add/", json={
            "product_id": p['id'],
            "user_id": App.get_running_app().user_id
        })


# =========================
# 🛒 CART
# =========================
class CartScreen(Screen):
    def on_enter(self):
        self.load()

    def popup(self, text):
        Popup(title="Info", content=Label(text=text), size_hint=(0.6, 0.3)).open()

    def load(self):
        self.clear_widgets()

        main = BoxLayout(orientation='vertical')

        scroll = ScrollView()
        layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(10))
        layout.bind(minimum_height=layout.setter('height'))

        data = requests.get(f"{API_URL}/api/cart/?user_id={App.get_running_app().user_id}").json()
        total = data.get('total', 0)

        for item in data['items']:
            box = BoxLayout(size_hint_y=None, height=dp(100))

            box.opacity = 0
            Animation(opacity=1, duration=0.3).start(box)

            info = BoxLayout(orientation='vertical')
            info.add_widget(Label(text=item['name']))
            info.add_widget(Label(text=f"{item['price']}€"))

            qty = BoxLayout(size_hint_y=None, height=dp(40))

            minus = Button(text="-")
            plus = Button(text="+")
            lbl = Label(text=str(item['quantity']))

            minus.bind(on_press=lambda x, i=item: self.update(i['id'], "minus"))
            plus.bind(on_press=lambda x, i=item: self.update(i['id'], "plus"))

            qty.add_widget(minus)
            qty.add_widget(lbl)
            qty.add_widget(plus)

            info.add_widget(qty)

            remove = Button(text="✕", size_hint=(None, None), size=(dp(40), dp(40)))
            remove.bind(on_press=lambda x, i=item: self.remove(i['id']))

            box.add_widget(info)
            box.add_widget(remove)

            layout.add_widget(box)

        scroll.add_widget(layout)

        bottom = BoxLayout(size_hint_y=None, height=dp(100))

        bottom.add_widget(Label(text=f"Total: {total}€"))

        pay = Button(text="💳 Pay")
        pay.bind(on_press=lambda x: setattr(self.manager, 'current', 'payment'))

        back = Button(text="Back")
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'products'))

        bottom.add_widget(pay)
        bottom.add_widget(back)

        main.add_widget(scroll)
        main.add_widget(bottom)

        self.add_widget(main)

    def update(self, item_id, action):
        requests.post(f"{API_URL}/api/cart/update/", json={
            "item_id": item_id,
            "action": action
        })
        self.load()

    def remove(self, item_id):
        requests.post(f"{API_URL}/api/cart/remove/", json={"item_id": item_id})
        self.popup("Removed")
        self.load()


# =========================
# 💳 PAYMENT
# =========================
class PaymentScreen(Screen):
    def on_enter(self):
        self.clear_widgets()

        layout = BoxLayout(orientation='vertical', padding=dp(20), spacing=dp(10))

        self.card = TextInput(hint_text="Card number")
        self.expiry = TextInput(hint_text="MM/YY")
        self.cvv = TextInput(hint_text="CVV")

        self.msg = Label(text="")

        pay = Button(text="Pay", size_hint_y=None, height=dp(50))
        back = Button(text="Back", size_hint_y=None, height=dp(50))

        pay.bind(on_press=self.pay)
        back.bind(on_press=lambda x: setattr(self.manager, 'current', 'cart'))

        layout.add_widget(Label(text="Payment", font_size='20sp'))
        layout.add_widget(self.card)
        layout.add_widget(self.expiry)
        layout.add_widget(self.cvv)
        layout.add_widget(self.msg)
        layout.add_widget(pay)
        layout.add_widget(back)

        self.add_widget(layout)

    def pay(self, instance):
        try:
            res = requests.post(f"{API_URL}/api/checkout/", json={
                "user_id": App.get_running_app().user_id
            })

            data = res.json()

            if "order_id" in data:
                self.msg.text = "Payment successful ✔"
            else:
                self.msg.text = "Error"

        except:
            self.msg.text = "Server error"


# =========================
# 🚀 APP
# =========================
class MyApp(App):
    user_id = None

    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(ProductScreen(name='products'))
        sm.add_widget(CartScreen(name='cart'))
        sm.add_widget(PaymentScreen(name='payment'))

        sm.current = 'login'
        return sm


if __name__ == "__main__":
    MyApp().run()