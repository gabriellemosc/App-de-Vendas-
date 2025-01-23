import requests
from kivy.app import App    #to acess the app

class MyFirebase():
    API_KEY = ""

    def criar_conta(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.API_KEY}'  #link of our API

        info = {"email": email, "password":senha, "returnSecureToken": True}
        print(email, senha)

        requisicao = requests.post(link, data=info)     #we get the response to this request

        requisicao_dic = requisicao.json()  #turn into a python dictionary

        if requisicao.ok:
            print("Usuário Criado")
            refresh_token = requisicao_dic['refreshToken']    #authentication
            local_id = requisicao_dic['localId']           #user id 
            id_token = requisicao_dic['refreshToken']     #keep the user logged in

            meu_aplicativo = App.get_running_app()          #app that is running
            meu_aplicativo.local_id = local_id              
            meu_aplicativo.id_token = id_token

            #takes the 'refresh token' variable and writes it to a file
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)
            
            req_id = requests.get(f"https://aplicativovedas-default-rtdb.firebaseio.com/proximo_id_vendedor.json?auth={id_token}")
            id_vendedor = req_id.json()
            print(id_vendedor)

            link = f'https://aplicativovedas-default-rtdb.firebaseio.com/{local_id}.json?auth={id_token}'
            info_usuario = f'{{"avatar":"foto1.png", "equipe": "", "total_vendas":"","vendas": "", "id_vendedor": "{id_vendedor}"}}'
            requisicao_usuario = requests.patch(link, data=info_usuario)

            #update the id of the next seller
            proximo_id_vendedor = int(id_vendedor) + 1
            info_id_vendedor = f'{{"proximo_id_vendedor": "{proximo_id_vendedor}"}}'
            requests.patch(f"https://aplicativovedas-default-rtdb.firebaseio.com/.json?auth={id_token}", data=info_id_vendedor) 
            
            #We load user information after creating account
            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")
        else:  
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()          #response from the app that is running
            pagina_login = meu_aplicativo.root.ids['loginpage'] #id from loginpage
            pagina_login.ids['mensagem_login'].text = mensagem_erro #acess the text from 'mensagem_login' and change
            pagina_login.ids['mensagem_login'].color = (1,0,0,1)

        print(requisicao_dic)

    def fazer_login(self, email, senha):
        link = f'https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={self.API_KEY}'
        info = {"email": email, "password":senha, "returnSecureToken": True}

        requisicao = requests.post(link, data=info)     #we get the response to this request

        requisicao_dic = requisicao.json()  #turn into a python dictionary

        if requisicao.ok:
            refresh_token = requisicao_dic['refreshToken']    #authentication
            local_id = requisicao_dic['localId']           #user id 
            id_token = requisicao_dic['refreshToken']     #keep the user logged in

            meu_aplicativo = App.get_running_app()          #app that is running
            meu_aplicativo.local_id = local_id              
            meu_aplicativo.id_token = id_token

            #takes the 'refresh token' variable and writes it to a file
            with open("refreshtoken.txt", "w") as arquivo:
                arquivo.write(refresh_token)
            
            #We load user information after creating account
            meu_aplicativo.carregar_infos_usuario()
            meu_aplicativo.mudar_tela("homepage")
        else:  
            mensagem_erro = requisicao_dic['error']['message']
            meu_aplicativo = App.get_running_app()          #response from the app that is running
            pagina_login = meu_aplicativo.root.ids['loginpage'] #id from loginpage
            pagina_login.ids['mensagem_login'].text = mensagem_erro #acess the text from 'mensagem_login' and change
            pagina_login.ids['mensagem_login'].color = (1,0,0,1)

        print(requisicao_dic)



    def trocar_token(self, refresh_token):
        link = f'https://securetoken.googleapis.com/v1/token?key={self.API_KEY}'

        info = {"grant_type":"refresh_token",
                "refresh_token":refresh_token
                }
        requisicao = requests.post(link, data=info)
        requisicao_dic = requisicao.json()
        if 'error' in requisicao_dic:
            print(f"Erro ao trocar token:{requisicao_dic['error']['message']}")
            return None, None
        
        local_id = requisicao_dic['user_id']
        id_token = requisicao_dic['id_token']
        print("Novo Token Gerado")

        return local_id, id_token
