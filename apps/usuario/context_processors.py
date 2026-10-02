from django.db.utils import OperationalError, ProgrammingError
from .models import PerfilUsuario


def usuario_perfil(request):
    perfil = None

    if request.user.is_authenticated:
        try:
            perfil = (
                PerfilUsuario.objects
                .select_related('mercadinho')
                .filter(usuario=request.user)
                .first()
            )
        except (OperationalError, ProgrammingError):
            perfil = None

    return {
        'perfil_usuario': perfil
    }
