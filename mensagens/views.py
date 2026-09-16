# from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponse

# from .bst_core import criptografar_mensagem      # ajustar import certo
# from .bst_visualizacao import gerar_imagem_arvore

#@login_required
def criptografar(request):
    contexto = {}

    if request.method == 'POST' and request.POST.get('acao') == 'criptografar':
        email_destinatario = request.POST.get('email')
        mensagem = request.POST.get('mensagem')

        # TODO: chamar a função real do bst_core.py aqui
        # mensagem_cifrada, arvore = criptografar_mensagem(mensagem, email_destinatario)
        # imagem_path = gerar_imagem_arvore(arvore)

        # guarda na sessão pra "Salvar" saber o que gravar, sem recriptografar
        #request.session['mensagem_cifrada'] = mensagem_cifrada
        request.session['email_destinatario'] = email_destinatario

        #contexto['mensagem_cifrada'] = mensagem_cifrada
        #contexto['imagem_arvore'] = imagem_path

    return render(request, 'criptografar.html', contexto)


#@login_required
def salvar_arquivo(request):
    mensagem_cifrada = request.session.get('mensagem_cifrada')

    if not mensagem_cifrada:
        return HttpResponse(status=400) 

    response = HttpResponse(mensagem_cifrada, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="mensagem_cifrada.txt"'
    return response

#@login_required
def descriptografar(request):
    return render(request, 'descriptografar.html', {})