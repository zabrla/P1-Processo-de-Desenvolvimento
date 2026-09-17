import os
import uuid

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render

from utilils.bst.bst_visualizacao import gerar_imagem_cripto, gerar_imagem_decripto
from .models import LogAuditoria

#@login_required
def criptografar(request):
    contexto = {}

    if request.method == 'POST' and request.POST.get('acao') == 'criptografar':
        email_destinatario = request.POST.get('email')
        mensagem = request.POST.get('mensagem')

        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        nome_imagem = f"{uuid.uuid4().hex}.png"
        caminho_imagem = os.path.join(settings.MEDIA_ROOT, nome_imagem)

        # a chave usada pra cifrar e o email do destinatario -- so quem
        # logar com esse mesmo email consegue decifrar (ver view abaixo)
        resultado = gerar_imagem_cripto(email_destinatario, mensagem, caminho_imagem)

        request.session['mensagem_cifrada'] = resultado['cifra']
        request.session['email_destinatario'] = email_destinatario

        contexto['mensagem_cifrada'] = resultado['cifra']
        contexto['imagem_arvore'] = settings.MEDIA_URL + nome_imagem

        LogAuditoria.objects.create(
            usuario=request.user,
            acao='CIFROU',
            detalhes=f"Destinatário definido: {email_destinatario}"
        )

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
    contexto = {}
    mensagem = ''

    if request.method == 'POST':
        acao = request.POST.get('acao')

        if acao == 'importar':
            arquivo = request.FILES.get('arquivo')
            if arquivo:
                mensagem = arquivo.read().decode('utf-8')
            contexto['mensagem'] = mensagem

        elif acao == 'descriptografar':
            mensagem = request.POST.get('mensagem')
            contexto['mensagem'] = mensagem

            os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
            nome_imagem = f"{uuid.uuid4().hex}.png"
            caminho_imagem = os.path.join(settings.MEDIA_ROOT, nome_imagem)

            try:
                # a chave pra decifrar e o email de quem esta logado
                resultado = gerar_imagem_decripto(request.user.email, mensagem, caminho_imagem)
                contexto['mensagem_decifrada'] = resultado['texto']
                contexto['imagem_arvore'] = settings.MEDIA_URL + nome_imagem

                LogAuditoria.objects.create(
                    usuario=request.user,
                    acao='DECIFROU_SUCESSO',
                    detalhes="Mensagem descriptografada com sucesso."
                )
            except Exception:
                contexto['erro'] = 'Não foi possível descriptografar essa mensagem com o seu e-mail.'

            LogAuditoria.objects.create(
                    usuario=request.user,
                    acao='DECIFROU_NEGADO',
                    detalhes="Falha na leitura: E-mail não autorizado ou mensagem inválida."
                )

    return render(request, 'descriptografar.html', contexto)


# @login_required
def historico_logs(request):
    if request.user.is_staff:
        logs = LogAuditoria.objects.all().order_by('-criado_em')
    else:
        logs = LogAuditoria.objects.filter(usuario=request.user).order_by('-criado_em')

    return render(request, 'logs.html', {'logs': logs})