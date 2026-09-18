from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db import models

class LogAuditoria(models.Model):
    ACAO_CHOICES = [
        ('CIFROU', 'Criptografar'),
        ('DECIFROU_SUCESSO', 'Descriptografar - Sucesso'),
        ('DECIFROU_NEGADO', 'Descriptografar - Acesso Negado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=30, choices=ACAO_CHOICES)
    detalhes = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.email} - {self.get_acao_display()} ({self.criado_em.strftime('%d/%m/%Y %H:%M')})"

class Mensagem(models.Model):
    remetente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mensagens_enviadas',
    )
    email_destinatario = models.EmailField()
    conteudo_cifrado = models.TextField()
    data_envio = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.remetente} -> {self.email_destinatario} ({self.data_envio:%d/%m/%Y %H:%M})"