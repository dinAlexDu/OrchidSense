from models import UserConfig

def verificar_configuracoes():
    configs = UserConfig.query.all()

    for config in configs:
        temperatura_medida = ...
        humidade_medida = ...

        if (temperatura_medida < config.temp_min or temperatura_medida > config.temp_max) or \
           (humidade_medida < config.humidade_min or humidade_medida > config.humidade_max):
            enviar_notificacao(config.user_id)

