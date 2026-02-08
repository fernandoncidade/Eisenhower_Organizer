from .incore_01_initUI import init_ui
from .incore_02_add_placeholder import add_placeholder
from .incore_03_criar_menu_configuracoes import criar_menu_configuracoes
from .incore_04_definir_idioma import definir_idioma
from .incore_05_atualizar_textos import atualizar_textos
from .incore_06_atualizar_placeholders import atualizar_placeholders
from .incore_07_MostrarMenuContexto import MostrarMenuContexto, show_context_menu
from .incore_08_exibir_sobre import exibir_sobre
from .incore_09_Arquivo import Arquivo
from .incore_13_prioridade_display import prioridade_para_texto
from .incore_12_Manual import (
	normalize_language,
	get_manual_title,
	get_manual_document,
	get_manual_blocks,
	get_manual_text,
	get_manual_text_with_positions,
)

__all__ = [
	"init_ui",
	"add_placeholder",
	"criar_menu_configuracoes",
	"definir_idioma",
	"atualizar_textos",
	"atualizar_placeholders",
	"MostrarMenuContexto",
	"show_context_menu",
	"exibir_sobre",
	"Arquivo",
	"prioridade_para_texto",
	"normalize_language",
	"get_manual_title",
	"get_manual_document",
	"get_manual_blocks",
	"get_manual_text",
	"get_manual_text_with_positions",
]
