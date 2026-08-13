import os, sqlite3, csv
from datetime import datetime
from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup

DB = "pos.db"

def db():
    return sqlite3.connect(DB)

def init_db():
    c = db()
    x = c.cursor()
    x.execute("""CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        barcode TEXT UNIQUE,
        name TEXT NOT NULL,
        price INTEGER NOT NULL,
        stock INTEGER NOT NULL DEFAULT 0)""")
    x.execute("""CREATE TABLE IF NOT EXISTS transactions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT, total INTEGER, paid INTEGER, change INTEGER)""")
    x.execute("""CREATE TABLE IF NOT EXISTS items(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id INTEGER, product_id INTEGER,
        name TEXT, price INTEGER, qty INTEGER, subtotal INTEGER)""")
    c.commit(); c.close()

def rupiah(n):
    return "Rp {:,}".format(int(n)).replace(",", ".")

class POSApp(App):
    def build(self):
        init_db()
        self.cart = []
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))

        header = BoxLayout(size_hint_y=None, height=dp(55), spacing=dp(6))
        header.add_widget(Label(text="[b]KASIR POS[/b]", markup=True, font_size=dp(21)))
        b = Button(text="Laporan", size_hint_x=None, width=dp(100))
        b.bind(on_press=self.report)
        header.add_widget(b)
        root.add_widget(header)

        body = BoxLayout(spacing=dp(8))
        left = BoxLayout(orientation="vertical", spacing=dp(5))
        self.search = TextInput(hint_text="Cari nama / barcode...", size_hint_y=None, height=dp(42))
        self.search.bind(text=lambda *_: self.refresh_products())
        left.add_widget(self.search)
        sv = ScrollView()
        self.products = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.products.bind(minimum_height=self.products.setter("height"))
        sv.add_widget(self.products); left.add_widget(sv)
        body.add_widget(left)

        right = BoxLayout(orientation="vertical", spacing=dp(5))
        right.add_widget(Label(text="[b]KERANJANG[/b]", markup=True, size_hint_y=None, height=dp(30)))
        sv2 = ScrollView()
        self.cart_view = GridLayout(cols=1, spacing=dp(4), size_hint_y=None)
        self.cart_view.bind(minimum_height=self.cart_view.setter("height"))
        sv2.add_widget(self.cart_view); right.add_widget(sv2)
        self.total = Label(text="TOTAL: Rp 0", font_size=dp(19), size_hint_y=None, height=dp(40))
        right.add_widget(self.total)
        self.paid = TextInput(hint_text="Uang dibayar", input_filter="int", size_hint_y=None, height=dp(42))
        right.add_widget(self.paid)
        pay = Button(text="BAYAR & SIMPAN STRUK", size_hint_y=None, height=dp(50))
        pay.bind(on_press=self.checkout); right.add_widget(pay)
        clear = Button(text="Kosongkan", size_hint_y=None, height=dp(40))
        clear.bind(on_press=lambda *_: self.clear_cart()); right.add_widget(clear)
        body.add_widget(right)
        root.add_widget(body)

        add = Button(text="+ TAMBAH PRODUK", size_hint_y=None, height=dp(48))
        add.bind(on_press=self.add_product_popup); root.add_widget(add)
        self.refresh_products()
        return root

    def refresh_products(self):
        self.products.clear_widgets()
        q = self.search.text.lower()
        c = db(); rows = c.execute("SELECT id,barcode,name,price,stock FROM products ORDER BY name").fetchall(); c.close()
        for p in rows:
            if q and q not in (p[1] or "").lower() and q not in p[2].lower(): continue
            btn = Button(text=f"{p[2]}\n{rupiah(p[3])} | Stok {p[4]}", size_hint_y=None, height=dp(62))
            btn.bind(on_press=lambda _, p=p: self.add_to_cart(p))
            self.products.add_widget(btn)

    def add_to_cart(self, p):
        if p[4] <= 0: return self.msg("Stok habis", "Produk tidak memiliki stok.")
        for i in self.cart:
            if i["id"] == p[0]:
                if i["qty"] >= p[4]: return self.msg("Stok tidak cukup", "Jumlah melebihi stok.")
                i["qty"] += 1; i["subtotal"] = i["qty"]*i["price"]; self.refresh_cart(); return
        self.cart.append({"id":p[0],"name":p[2],"price":p[3],"qty":1,"subtotal":p[3]})
        self.refresh_cart()

    def refresh_cart(self):
        self.cart_view.clear_widgets(); total=0
        for idx,i in enumerate(self.cart):
            total += i["subtotal"]
            row=BoxLayout(size_hint_y=None,height=dp(48))
            row.add_widget(Label(text=f"{i['name']} x{i['qty']}\n{rupiah(i['subtotal'])}"))
            m=Button(text="-",size_hint_x=None,width=dp(45))
            m.bind(on_press=lambda _, idx=idx: self.minus(idx)); row.add_widget(m)
            self.cart_view.add_widget(row)
        self.total.text=f"TOTAL: {rupiah(total)}"

    def minus(self, idx):
        if self.cart[idx]["qty"] > 1:
            self.cart[idx]["qty"]-=1
            self.cart[idx]["subtotal"]=self.cart[idx]["qty"]*self.cart[idx]["price"]
        else: self.cart.pop(idx)
        self.refresh_cart()

    def clear_cart(self):
        self.cart=[]; self.refresh_cart(); self.paid.text=""

    def checkout(self, *_):
        if not self.cart: return self.msg("Keranjang kosong","Tambahkan produk terlebih dahulu.")
        try: paid=int(self.paid.text)
        except: return self.msg("Pembayaran","Masukkan uang pembayaran.")
        total=sum(i["subtotal"] for i in self.cart)
        if paid<total: return self.msg("Uang kurang",f"Total {rupiah(total)}")
        change=paid-total
        c=db(); x=c.cursor(); now=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        x.execute("INSERT INTO transactions(date,total,paid,change) VALUES(?,?,?,?)",(now,total,paid,change))
        tid=x.lastrowid
        for i in self.cart:
            x.execute("INSERT INTO items(transaction_id,product_id,name,price,qty,subtotal) VALUES(?,?,?,?,?,?)",
                      (tid,i["id"],i["name"],i["price"],i["qty"],i["subtotal"]))
            x.execute("UPDATE products SET stock=stock-? WHERE id=?",(i["qty"],i["id"]))
        c.commit(); c.close()
        path=self.make_receipt(tid,total,paid,change)
        self.msg("Transaksi berhasil",f"Total: {rupiah(total)}\nKembalian: {rupiah(change)}\n\nStruk tersimpan di:\n{path}")
        self.clear_cart(); self.refresh_products()

    def make_receipt(self, tid,total,paid,change):
        out=os.path.join(App.get_running_app().user_data_dir,f"struk_{tid}.txt")
        with open(out,"w",encoding="utf-8") as f:
            f.write("TOKO SAYA\n"+"="*32+"\n")
            for i in self.cart: f.write(f"{i['name']} x{i['qty']}  {rupiah(i['subtotal'])}\n")
            f.write("="*32+f"\nTOTAL     {rupiah(total)}\nBAYAR     {rupiah(paid)}\nKEMBALI   {rupiah(change)}\n\nTerima kasih\n")
        return out

    def add_product_popup(self,*_):
        box=BoxLayout(orientation="vertical",padding=dp(10),spacing=dp(7))
        barcode=TextInput(hint_text="Barcode"); name=TextInput(hint_text="Nama produk")
        price=TextInput(hint_text="Harga",input_filter="int"); stock=TextInput(hint_text="Stok",input_filter="int")
        save=Button(text="Simpan",size_hint_y=None,height=dp(45))
        for w in (barcode,name,price,stock,save): box.add_widget(w)
        pop=Popup(title="Tambah Produk",content=box,size_hint=(.9,.72))
        def do(_):
            if not name.text or not price.text: return self.msg("Error","Nama dan harga wajib diisi.")
            c=db()
            try:
                c.execute("INSERT INTO products(barcode,name,price,stock) VALUES(?,?,?,?)",
                          (barcode.text or None,name.text,int(price.text),int(stock.text or 0)))
                c.commit(); pop.dismiss(); self.refresh_products()
            except sqlite3.IntegrityError: self.msg("Error","Barcode sudah digunakan.")
            finally: c.close()
        save.bind(on_press=do); pop.open()

    def report(self,*_):
        out=os.path.join(App.get_running_app().user_data_dir,"laporan_penjualan.csv")
        c=db(); rows=c.execute("SELECT id,date,total,paid,change FROM transactions ORDER BY id DESC").fetchall(); c.close()
        with open(out,"w",newline="",encoding="utf-8-sig") as f:
            w=csv.writer(f); w.writerow(["ID","Tanggal","Total","Bayar","Kembalian"]); w.writerows(rows)
        self.msg("Laporan dibuat",out)

    def msg(self,title,text):
        box=BoxLayout(orientation="vertical",padding=dp(8))
        box.add_widget(Label(text=text))
        b=Button(text="OK",size_hint_y=None,height=dp(42)); box.add_widget(b)
        p=Popup(title=title,content=box,size_hint=(.88,.42)); b.bind(on_press=p.dismiss); p.open()

if __name__=="__main__":
    POSApp().run()
