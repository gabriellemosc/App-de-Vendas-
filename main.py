from kivy.app import App
from kivy.lang import Builder   #build the app
from telas import *             #import all from telas
from botoes import *
import requests
import os
import certifi
from bannervenda import BannerVenda
import os       #navigate between our project files
from functools import partial   
from myfirebase import *
from bannervendedor import BannerVendedor
from datetime import date

os.environ["SSL.CERT_FILE"] = certifi.where()


GUI = Builder.load_file("main.kv")      #load the graphical interface
class MainApp(App):
    cliente = None
    produto = None
    unidade = None


    def build(self):        #build the app
        self.firebase = MyFirebase()        #our file,  import the class, with all its attributes
        return GUI          #return the app
    
    def on_start(self):     #exe when start the app
        #load photos 
        arquivos = os.listdir(r"icones/fotos_perfil")   #list our photos inside the folder
        pagina_foto_perfil = self.root.ids["fotoperfilpage"]
        lista_fotos = pagina_foto_perfil.ids["lista_fotos_perfil"]
        for foto in arquivos:
            imagem = ImageButton(source=f"icones/fotos_perfil/{foto}", on_release=partial(self.mudar_foto_perfil, foto))
            lista_fotos.add_widget(imagem)

        #load customers's photos
        arquivos = os.listdir("icones/fotos_clientes")
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionar_vendas.ids['lista_clientes']

        for foto_cliente in arquivos:
             imagem = ImageButton(source=f"icones/fotos_clientes/{foto_cliente}",on_release=partial(self.selecionar_cliente, foto_cliente))
             label = LabelButton(text=foto_cliente.replace(".png","").capitalize(), on_release=partial(self.selecionar_cliente, foto_cliente))
             lista_clientes.add_widget(imagem)
             lista_clientes.add_widget(label)
             
        #load product's photos
        arquivos = os.listdir("icones/fotos_produtos")
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_adicionar_vendas.ids['lista_produtos']

        for foto_produto in arquivos:
             imagem = ImageButton(source=f"icones/fotos_produtos/{foto_produto}", on_release=partial(self.selecionar_produto, foto_produto))
             label = LabelButton(text=foto_produto.replace(".png","").capitalize(), on_release=partial(self.selecionar_produto, foto_produto))
             lista_produtos.add_widget(imagem)
             lista_produtos.add_widget(label)

        #load date
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        label_data = pagina_adicionar_vendas.ids['label_data']
        label_data.text = f"Data: {date.today().strftime('%d/%m/%Y')}"

        self.carregar_infos_usuario()
        self.mudar_tela("homepage") 

     #update user infos 
    def carregar_infos_usuario(self):
        try:
            with open("refreshtoken.txt", "r") as arquivo:
                refresh_token = arquivo.read()
                if not refresh_token:
                    raise Exception("Token Vazio")
                #updates the access token
                local_id, id_token = self.firebase.trocar_token(refresh_token)  
                self.local_id = local_id
                self.id_token = id_token

                #get user info
                requisicao = requests.get(f'https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}')   #where our datas are
                requisicao_dic = requisicao.json()
                #profile picture
                avatar = requisicao_dic['avatar']                       #we get the information about the photo of the user
                self.avatar = avatar                                    #store the value of user attributes in the class itself, to be used later
                foto_perfil = self.root.ids["foto_perfil"]              #the item photo that we're changing
                foto_perfil.source = f"icones/fotos_perfil/{avatar}"    #dinamic form to change the profile picture


                #unique id

                id_vendedor = requisicao_dic['id_vendedor']
                self.id_vendedor = id_vendedor
                pagina_ajustes = self.root.ids["ajustespages"]
                pagina_ajustes.ids['id_vendedor'].text = f"Seu ID Único: {id_vendedor}"


                #total user sales
                total_vendas = requisicao_dic['total_vendas']
                self.total_vendas = total_vendas
                homepage = self.root.ids['homepage']
                homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

                #team
                self.equipe = requisicao_dic['equipe']

            #sales of the user
            try:
                vendas = requisicao_dic['vendas']
                self.vendas = vendas
                pagina_homepage = self.root.ids['homepage']             #get all the ids from homepage part in homepage.kv
                lista_vendas = pagina_homepage.ids['lista_vendas']      #get the list of sales 
                for id_venda in vendas:
                    venda = vendas[id_venda]
                    banner = BannerVenda(cliente=venda['cliente'], foto_cliente = venda['foto_cliente'], produto=venda['produto'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], unidade=venda['unidade'], quantidade=venda['quantidade'])
                    lista_vendas.add_widget(banner)                         # we add the banner infomations in our list
                #self.mudar_tela("homepage") 

            
                
            except Exception as excecao:
                   print(excecao)

            #user team  
            equipe = requisicao_dic['equipe']
            
            lista_equipe = equipe.split(',')
            
            pagina_listavendedores = self.root.ids['listarvendedorespage']
            lista_vendedores = pagina_listavendedores.ids['lista_vendedores']   
            for id_vendedor_equipe in lista_equipe:
                if id_vendedor_equipe != "":
                    banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_equipe)
                    lista_vendedores.add_widget(banner_vendedor)
        
            
            
        except:
            pass
        
    
    def mudar_tela(self,id_tela ):       #change screen, we must pass the id as a parameter
        gerenciador_telas =  self.root.ids['screen_manager']          #the main file kv
        gerenciador_telas.current = id_tela                           #change the screen, using the id as parameter

    #change profile photo
    def mudar_foto_perfil(self, foto, *args):
        foto_perfil = self.root.ids["foto_perfil"]              #the item photo that we're changing
        foto_perfil.source = f"icones/fotos_perfil/{foto}"    #dinamic form to change the profile picture
            #update the profile photo in the Database
        info = f'{{"avatar": "{foto}"}}'
        requisicao = requests.patch(f"https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",
                                    data=info)
        
        self.mudar_tela("ajustespages")
    #add salesperson to team
    def adicionar_vendedor(self, id_vendedor_adicionado):
            # Remover quebras de linha e espaços extras
            id_vendedor_adicionado = id_vendedor_adicionado.strip()
            link = f'https://aplicativovedas-default-rtdb.firebaseio.com/.json?orderBy=%22id_vendedor%22&equalTo=%22{id_vendedor_adicionado}%22'
            requisicao = requests.get(link)
            requisicao_dic = requisicao.json()
            pagina_adicionar_vendedor = self.root.ids['adicionarvendedorpage']
            mensagem_texto = pagina_adicionar_vendedor.ids['mensagem_outrovendedor']
            #if there is nothing in the dictionary
            if requisicao_dic == {}:
                    mensagem_texto.text = "Usuário Não Encontrado"
            else:
                 equipe = self.equipe.split(",")
                 if id_vendedor_adicionado in equipe:
                      mensagem_texto.text = "Vendedor Já Faz Parte da Equipe"
                 else:
                      self.equipe = self.equipe + f",{id_vendedor_adicionado}"
                      info = f'{{"equipe":"{self.equipe}"}}'
                      requests.patch(f'https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}', data=info) 
                      mensagem_texto.text = "Vendedor Adicionado com Sucesso"
                      # add a new banner to the salesman
                      pagina_listavendedores = self.root.ids['listarvendedorespage']
                      lista_vendedores = pagina_listavendedores.ids['lista_vendedores'] 
                      banner_vendedor = BannerVendedor(id_vendedor=id_vendedor_adicionado)
                      lista_vendedores.add_widget(banner_vendedor)
#select customer, on the add sales page
    def selecionar_cliente(self, foto, *args):
        self.cliente = foto.replace(".png","")

        #paint the other letters white
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_clientes = pagina_adicionar_vendas.ids['lista_clientes']

        for item in list(lista_clientes.children):
             item.color = (1, 1, 1, 1)
          #paint the letter we selected blue
             try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                     item.color =   (0,207/255,219/255,1)       #color blue
             except:
               pass
             

    def selecionar_produto(self, foto, *args):
        self.produto = foto.replace(".png","")
        #paint the other letters white
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        lista_produtos = pagina_adicionar_vendas.ids['lista_produtos']

        for item in list(lista_produtos.children):
             item.color = (1, 1, 1, 1)
          #paint the letter we selected blue
             try:
                texto = item.text
                texto = texto.lower() + ".png"
                if foto == texto:
                     item.color =   (0,207/255,219/255,1)       #color blue
             except:
               pass   
             
    def selecionar_unidade(self, id_label, *args):
        pagina_adicionar_vendas = self.root.ids['adicionarvendaspage']
        self.unidade = id_label.replace("unidades_", "")
        #paint the other letters white
        pagina_adicionar_vendas.ids['unidades_kg'].color = (1,1,1,1)
        pagina_adicionar_vendas.ids['unidades_unidades'].color = (1,1,1,1)
        pagina_adicionar_vendas.ids['unidades_litros'].color = (1,1,1,1)

          #paint the letter we selected blue
        pagina_adicionar_vendas.ids[id_label].color = (0,207/255,219/255,1)  


#add sale to our database
    def adicionar_venda(self):
        cliente = self.cliente
        produto = self.produto
        unidade = self.unidade

        #get date
        pagina_adicionar_vendas = self.root.ids["adicionarvendaspage"]
        data = pagina_adicionar_vendas.ids['label_data'].text.replace("Data: ", "")
        preco = pagina_adicionar_vendas.ids['preco_total'].text
        quantidade = pagina_adicionar_vendas.ids['quantidade'].text

        #check if these fields are filled in
        if not cliente:
            pagina_adicionar_vendas.ids['label_selecione_cliente'].color = (1,0,0,1)
        if not produto:
            pagina_adicionar_vendas.ids['label_selecione_produto'].color = (1,0,0,1)
        if not unidade:
            pagina_adicionar_vendas.ids['unidades_kg'].color = (1,0,0,1)
            pagina_adicionar_vendas.ids['unidades_unidades'].color = (1,0,0,1)
            pagina_adicionar_vendas.ids['unidades_litros'].color = (1,0,0,1)
        if not preco:
            pagina_adicionar_vendas.ids['label_preco'].color = (1,0,0,1)
        else:
            try:
                preco = float(preco)
            except:
                pagina_adicionar_vendas.ids['label_preco'].color = (1,0,0,1)
        if not quantidade:
            pagina_adicionar_vendas.ids['label_quantidade'].color = (1,0,0,1)
        else:
            try:
                quantidade = float(quantidade)
            except:
                pagina_adicionar_vendas.ids['label_quantidade'].color = (1,0,0,1)
        #After the customer fills in all the fields, we will execute the execute sale code
        if cliente and produto and unidade and preco and quantidade and (type(preco) == float) and (type(quantidade) == float):
            foto_produto = produto + ".png"
            foto_cliente = cliente + ".png"
            # add a sales in DB
            info = f'{{"cliente": "{cliente}", "produto": "{produto}", "foto_cliente": "{foto_cliente}", ' \
            f'"foto_produto": "{foto_produto}","data": "{data}", "unidade": "{unidade}",'\
             f'"preco": "{preco}", "quantidade": "{quantidade}"}}' 
            
            requests.post(f"https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}/vendas.json?auth={self.id_token}",
                          data=info)
            
        #create banner based on the sale we made
            banner = BannerVenda(cliente=cliente, produto=produto, foto_cliente=foto_cliente, foto_produto=foto_produto, data=data, preco=preco, quantidade=quantidade, unidade=unidade)
            pagina_homepage = self.root.ids["homepage"]
            lista_vendas = pagina_homepage.ids["lista_vendas"]
            lista_vendas.add_widget(banner)
            

            #update total sales field
            requisicao = requests.get(f"https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}/total_vendas.json?auth={self.id_token}")
            try:
                total_vendas = float(requisicao.json())
            except ValueError:
                total_vendas = 0
            total_vendas += preco

            info = f'{{"total_vendas": "{total_vendas}"}}'
            requests.patch(f"https://aplicativovedas-default-rtdb.firebaseio.com/{self.local_id}.json?auth={self.id_token}",data=info)
            #updates homepage value
            homepage = self.root.ids['homepage']
            homepage.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'
            print(total_vendas)
            
            self.mudar_tela("homepage")



        self.cliente = None
        self.produto = None
        self.unidade = None

    def carregar_todas_vendas(self):
                pagina_todas_vendas = self.root.ids['todasvendaspage']
                lista_vendas = pagina_todas_vendas.ids['lista_vendas']
                #so as not to repeat sales banners with each update
                for item in list(lista_vendas.children):
                     lista_vendas.remove_widget(item)
                 #get company info
                requisicao = requests.get(f'https://aplicativovedas-default-rtdb.firebaseio.com/.json?orderBy="id_vendedor"')   #where our datas are
                requisicao_dic = requisicao.json()
                #profile picture
                foto_perfil = self.root.ids["foto_perfil"]              #the item photo that we're changing
                foto_perfil.source = f"icones/fotos_perfil/hash.png"    #dinamic form to change the profile picture
                
                
                total_vendas = 0 
                for local_id_usuario in requisicao_dic:
                    try:
                        vendas = requisicao_dic[local_id_usuario]['vendas']
                        for id_venda in vendas:
                                venda = vendas[id_venda]
                                total_vendas += float(venda['preco'])
                                banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], quantidade=venda['quantidade'], unidade=venda['unidade'])
                                lista_vendas.add_widget(banner)
                    except:
                         pass



                #total user sales
                pagina_todas_vendas.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'



                self.mudar_tela("todasvendaspage")

    def sair_todas_vendas(self, id_tela):
          foto_perfil = self.root.ids["foto_perfil"]              #the item photo that we're changing
          foto_perfil.source = f"icones/fotos_perfil/{self.avatar}"    #dinamic form to change the profile picture

          self.mudar_tela(id_tela)

    #upload another seller's sales banners
    def carregar_vendas_vendedor(self, dic_info_vendedor, *args):
   
                    try:
                        vendas = dic_info_vendedor["vendas"]
                        pagina_vendasoutrovendedor = self.root.ids['vendasoutrovendedorpage']
                        lista_vendas = pagina_vendasoutrovendedor.ids['lista_vendas']
                        #clean old sales
                        for item in list(lista_vendas.children):
                            lista_vendas.remove_widget(item)
                        for id_venda in vendas:
                                venda = vendas[id_venda]
                                banner = BannerVenda(cliente=venda['cliente'], produto=venda['produto'], foto_cliente=venda['foto_cliente'], foto_produto=venda['foto_produto'], data=venda['data'], preco=venda['preco'], quantidade=venda['quantidade'], unidade=venda['unidade'])
                                lista_vendas.add_widget(banner)
                    except:
                         pass
                    total_vendas = dic_info_vendedor['total_vendas']
                      #total user sales
                    pagina_vendasoutrovendedor.ids['label_total_vendas'].text = f'[color=#000000]Total de Vendas:[/color] [b]R${total_vendas}[/b]'

                    #profile picture
                    foto_perfil = self.root.ids["foto_perfil"]              #the item photo that we're changing
                    avatar = dic_info_vendedor['avatar']
                    foto_perfil.source = f"icones/fotos_perfil/{avatar}"    #dinamic form to change the profile picture


         
                    self.mudar_tela('vendasoutrovendedorpage')
         
         



MainApp().run()         #ex the app


