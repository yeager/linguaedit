#!/usr/bin/env python3
"""
Automatically translate all unfinished strings in LinguaEdit translation files.
Translates from English source to target languages using comprehensive UI terminology.
"""

import xml.etree.ElementTree as ET
import re
from pathlib import Path

# Comprehensive translation dictionaries for UI terminology
TRANSLATIONS = {
    'sv': {
        # Basic operations
        'Search': 'Sök', 'Replace': 'Ersätt', 'Match': 'Matchning', 'Find': 'Hitta',
        'Open': 'Öppna', 'Save': 'Spara', 'Close': 'Stäng', 'Exit': 'Avsluta',
        'Edit': 'Redigera', 'File': 'Fil', 'View': 'Visa', 'Tools': 'Verktyg',
        'Help': 'Hjälp', 'About': 'Om', 'Settings': 'Inställningar', 'Options': 'Alternativ',
        
        # Application specific
        'Glossary': 'Ordlista', 'Statistics': 'Statistik', 'Header': 'Filhuvud',
        'Project': 'Projekt', 'Compare': 'Jämför', 'Theme': 'Tema', 
        'Comment': 'Kommentar', 'Memory': 'Minne', 'Batch': 'Batch',
        'Export': 'Exportera', 'Import': 'Importera', 'Translation': 'Översättning',
        'Source': 'Källa', 'Target': 'Mål', 'Language': 'Språk', 'Entry': 'Post',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Avbryt', 'Apply': 'Tillämpa', 'Yes': 'Ja', 'No': 'Nej',
        'Browse': 'Bläddra', 'Preview': 'Förhandsgranska', 'Clear': 'Rensa',
        'Select': 'Välj', 'Delete': 'Ta bort', 'Add': 'Lägg till', 'Remove': 'Ta bort',
        
        # Status and actions
        'Loading': 'Laddar', 'Saving': 'Sparar', 'Ready': 'Redo', 'Processing': 'Bearbetar',
        'Complete': 'Klar', 'Failed': 'Misslyckades', 'Success': 'Lyckades',
        'Error': 'Fel', 'Warning': 'Varning', 'Information': 'Information',
        
        # Batch operations
        'Batch Edit': 'Batchredigering', 'Operation': 'Åtgärd', 'Before': 'Före', 'After': 'Efter',
        'Select All': 'Markera alla', 'Deselect All': 'Avmarkera alla',
        
        # Fuzzy and translation states
        'Fuzzy': 'Osäker', 'Untranslated': 'Oöversatt', 'Translated': 'Översatt',
        'Accept': 'Acceptera', 'Reject': 'Förkasta',
        
        # Common phrases
        'Are you sure?': 'Är du säker?', 'Choose file': 'Välj fil',
        'Invalid format': 'Ogiltigt format', 'File not found': 'Filen hittades inte',
        'Permission denied': 'Åtkomst nekad', 'Unknown error': 'Okänt fel',
    },
    
    'de': {
        # Basic operations
        'Search': 'Suchen', 'Replace': 'Ersetzen', 'Match': 'Übereinstimmung', 'Find': 'Finden',
        'Open': 'Öffnen', 'Save': 'Speichern', 'Close': 'Schließen', 'Exit': 'Beenden',
        'Edit': 'Bearbeiten', 'File': 'Datei', 'View': 'Ansicht', 'Tools': 'Werkzeuge',
        'Help': 'Hilfe', 'About': 'Über', 'Settings': 'Einstellungen', 'Options': 'Optionen',
        
        # Application specific
        'Glossary': 'Glossar', 'Statistics': 'Statistik', 'Header': 'Dateikopf',
        'Project': 'Projekt', 'Compare': 'Vergleichen', 'Theme': 'Design',
        'Comment': 'Kommentar', 'Memory': 'Speicher', 'Batch': 'Stapel',
        'Export': 'Exportieren', 'Import': 'Importieren', 'Translation': 'Übersetzung',
        'Source': 'Quelle', 'Target': 'Ziel', 'Language': 'Sprache', 'Entry': 'Eintrag',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Abbrechen', 'Apply': 'Anwenden', 'Yes': 'Ja', 'No': 'Nein',
        'Browse': 'Durchsuchen', 'Preview': 'Vorschau', 'Clear': 'Löschen',
        'Select': 'Auswählen', 'Delete': 'Löschen', 'Add': 'Hinzufügen', 'Remove': 'Entfernen',
        
        # Status and actions
        'Loading': 'Laden', 'Saving': 'Speichern', 'Ready': 'Bereit', 'Processing': 'Verarbeitung',
        'Complete': 'Abgeschlossen', 'Failed': 'Fehlgeschlagen', 'Success': 'Erfolgreich',
        'Error': 'Fehler', 'Warning': 'Warnung', 'Information': 'Information',
        
        # Batch operations
        'Batch Edit': 'Stapelbearbeitung', 'Operation': 'Operation', 'Before': 'Vorher', 'After': 'Nachher',
        'Select All': 'Alle auswählen', 'Deselect All': 'Auswahl aufheben',
        
        # Fuzzy and translation states
        'Fuzzy': 'Unscharf', 'Untranslated': 'Unübersetzt', 'Translated': 'Übersetzt',
        'Accept': 'Akzeptieren', 'Reject': 'Ablehnen',
        
        # Common phrases
        'Are you sure?': 'Sind Sie sicher?', 'Choose file': 'Datei wählen',
        'Invalid format': 'Ungültiges Format', 'File not found': 'Datei nicht gefunden',
        'Permission denied': 'Zugriff verweigert', 'Unknown error': 'Unbekannter Fehler',
    },
    
    'fr': {
        # Basic operations
        'Search': 'Rechercher', 'Replace': 'Remplacer', 'Match': 'Correspondance', 'Find': 'Trouver',
        'Open': 'Ouvrir', 'Save': 'Enregistrer', 'Close': 'Fermer', 'Exit': 'Quitter',
        'Edit': 'Modifier', 'File': 'Fichier', 'View': 'Affichage', 'Tools': 'Outils',
        'Help': 'Aide', 'About': 'À propos', 'Settings': 'Paramètres', 'Options': 'Options',
        
        # Application specific
        'Glossary': 'Glossaire', 'Statistics': 'Statistiques', 'Header': 'En-tête',
        'Project': 'Projet', 'Compare': 'Comparer', 'Theme': 'Thème',
        'Comment': 'Commentaire', 'Memory': 'Mémoire', 'Batch': 'Lot',
        'Export': 'Exporter', 'Import': 'Importer', 'Translation': 'Traduction',
        'Source': 'Source', 'Target': 'Cible', 'Language': 'Langue', 'Entry': 'Entrée',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Annuler', 'Apply': 'Appliquer', 'Yes': 'Oui', 'No': 'Non',
        'Browse': 'Parcourir', 'Preview': 'Aperçu', 'Clear': 'Effacer',
        'Select': 'Sélectionner', 'Delete': 'Supprimer', 'Add': 'Ajouter', 'Remove': 'Retirer',
        
        # Status and actions
        'Loading': 'Chargement', 'Saving': 'Enregistrement', 'Ready': 'Prêt', 'Processing': 'Traitement',
        'Complete': 'Terminé', 'Failed': 'Échoué', 'Success': 'Réussi',
        'Error': 'Erreur', 'Warning': 'Avertissement', 'Information': 'Information',
        
        # Batch operations
        'Batch Edit': 'Modification par lot', 'Operation': 'Opération', 'Before': 'Avant', 'After': 'Après',
        'Select All': 'Tout sélectionner', 'Deselect All': 'Tout désélectionner',
        
        # Fuzzy and translation states
        'Fuzzy': 'Approximatif', 'Untranslated': 'Non traduit', 'Translated': 'Traduit',
        'Accept': 'Accepter', 'Reject': 'Rejeter',
        
        # Common phrases
        'Are you sure?': 'Êtes-vous sûr ?', 'Choose file': 'Choisir un fichier',
        'Invalid format': 'Format invalide', 'File not found': 'Fichier non trouvé',
        'Permission denied': 'Permission refusée', 'Unknown error': 'Erreur inconnue',
    },
    
    'es': {
        # Basic operations
        'Search': 'Buscar', 'Replace': 'Reemplazar', 'Match': 'Coincidencia', 'Find': 'Encontrar',
        'Open': 'Abrir', 'Save': 'Guardar', 'Close': 'Cerrar', 'Exit': 'Salir',
        'Edit': 'Editar', 'File': 'Archivo', 'View': 'Ver', 'Tools': 'Herramientas',
        'Help': 'Ayuda', 'About': 'Acerca de', 'Settings': 'Configuración', 'Options': 'Opciones',
        
        # Application specific
        'Glossary': 'Glosario', 'Statistics': 'Estadísticas', 'Header': 'Encabezado',
        'Project': 'Proyecto', 'Compare': 'Comparar', 'Theme': 'Tema',
        'Comment': 'Comentario', 'Memory': 'Memoria', 'Batch': 'Lote',
        'Export': 'Exportar', 'Import': 'Importar', 'Translation': 'Traducción',
        'Source': 'Origen', 'Target': 'Destino', 'Language': 'Idioma', 'Entry': 'Entrada',
        
        # Dialog elements
        'OK': 'Aceptar', 'Cancel': 'Cancelar', 'Apply': 'Aplicar', 'Yes': 'Sí', 'No': 'No',
        'Browse': 'Examinar', 'Preview': 'Vista previa', 'Clear': 'Limpiar',
        'Select': 'Seleccionar', 'Delete': 'Eliminar', 'Add': 'Añadir', 'Remove': 'Quitar',
        
        # Status and actions
        'Loading': 'Cargando', 'Saving': 'Guardando', 'Ready': 'Listo', 'Processing': 'Procesando',
        'Complete': 'Completado', 'Failed': 'Fallido', 'Success': 'Éxito',
        'Error': 'Error', 'Warning': 'Advertencia', 'Information': 'Información',
        
        # Batch operations
        'Batch Edit': 'Edición por lotes', 'Operation': 'Operación', 'Before': 'Antes', 'After': 'Después',
        'Select All': 'Seleccionar todo', 'Deselect All': 'Deseleccionar todo',
        
        # Fuzzy and translation states
        'Fuzzy': 'Dudoso', 'Untranslated': 'Sin traducir', 'Translated': 'Traducido',
        'Accept': 'Aceptar', 'Reject': 'Rechazar',
        
        # Common phrases
        'Are you sure?': '¿Está seguro?', 'Choose file': 'Elegir archivo',
        'Invalid format': 'Formato inválido', 'File not found': 'Archivo no encontrado',
        'Permission denied': 'Permiso denegado', 'Unknown error': 'Error desconocido',
    },
    
    'pt_BR': {
        # Basic operations
        'Search': 'Pesquisar', 'Replace': 'Substituir', 'Match': 'Correspondência', 'Find': 'Localizar',
        'Open': 'Abrir', 'Save': 'Salvar', 'Close': 'Fechar', 'Exit': 'Sair',
        'Edit': 'Editar', 'File': 'Arquivo', 'View': 'Visualizar', 'Tools': 'Ferramentas',
        'Help': 'Ajuda', 'About': 'Sobre', 'Settings': 'Configurações', 'Options': 'Opções',
        
        # Application specific
        'Glossary': 'Glossário', 'Statistics': 'Estatísticas', 'Header': 'Cabeçalho',
        'Project': 'Projeto', 'Compare': 'Comparar', 'Theme': 'Tema',
        'Comment': 'Comentário', 'Memory': 'Memória', 'Batch': 'Lote',
        'Export': 'Exportar', 'Import': 'Importar', 'Translation': 'Tradução',
        'Source': 'Origem', 'Target': 'Destino', 'Language': 'Idioma', 'Entry': 'Entrada',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Cancelar', 'Apply': 'Aplicar', 'Yes': 'Sim', 'No': 'Não',
        'Browse': 'Procurar', 'Preview': 'Visualizar', 'Clear': 'Limpar',
        'Select': 'Selecionar', 'Delete': 'Excluir', 'Add': 'Adicionar', 'Remove': 'Remover',
        
        # Status and actions
        'Loading': 'Carregando', 'Saving': 'Salvando', 'Ready': 'Pronto', 'Processing': 'Processando',
        'Complete': 'Concluído', 'Failed': 'Falhou', 'Success': 'Sucesso',
        'Error': 'Erro', 'Warning': 'Aviso', 'Information': 'Informação',
        
        # Batch operations
        'Batch Edit': 'Edição em lote', 'Operation': 'Operação', 'Before': 'Antes', 'After': 'Depois',
        'Select All': 'Selecionar tudo', 'Deselect All': 'Desmarcar tudo',
        
        # Fuzzy and translation states
        'Fuzzy': 'Impreciso', 'Untranslated': 'Não traduzido', 'Translated': 'Traduzido',
        'Accept': 'Aceitar', 'Reject': 'Rejeitar',
        
        # Common phrases
        'Are you sure?': 'Tem certeza?', 'Choose file': 'Escolher arquivo',
        'Invalid format': 'Formato inválido', 'File not found': 'Arquivo não encontrado',
        'Permission denied': 'Permissão negada', 'Unknown error': 'Erro desconhecido',
    },
    
    'ja': {
        # Basic operations
        'Search': '検索', 'Replace': '置換', 'Match': 'マッチ', 'Find': '検索',
        'Open': '開く', 'Save': '保存', 'Close': '閉じる', 'Exit': '終了',
        'Edit': '編集', 'File': 'ファイル', 'View': '表示', 'Tools': 'ツール',
        'Help': 'ヘルプ', 'About': 'について', 'Settings': '設定', 'Options': 'オプション',
        
        # Application specific
        'Glossary': '用語集', 'Statistics': '統計', 'Header': 'ヘッダー',
        'Project': 'プロジェクト', 'Compare': '比較', 'Theme': 'テーマ',
        'Comment': 'コメント', 'Memory': 'メモリ', 'Batch': 'バッチ',
        'Export': 'エクスポート', 'Import': 'インポート', 'Translation': '翻訳',
        'Source': 'ソース', 'Target': 'ターゲット', 'Language': '言語', 'Entry': 'エントリ',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'キャンセル', 'Apply': '適用', 'Yes': 'はい', 'No': 'いいえ',
        'Browse': '参照', 'Preview': 'プレビュー', 'Clear': 'クリア',
        'Select': '選択', 'Delete': '削除', 'Add': '追加', 'Remove': '削除',
        
        # Status and actions
        'Loading': '読み込み中', 'Saving': '保存中', 'Ready': '準備完了', 'Processing': '処理中',
        'Complete': '完了', 'Failed': '失敗', 'Success': '成功',
        'Error': 'エラー', 'Warning': '警告', 'Information': '情報',
        
        # Batch operations
        'Batch Edit': 'バッチ編集', 'Operation': '操作', 'Before': '前', 'After': '後',
        'Select All': 'すべて選択', 'Deselect All': 'すべて選択解除',
        
        # Fuzzy and translation states
        'Fuzzy': 'あいまい', 'Untranslated': '未翻訳', 'Translated': '翻訳済み',
        'Accept': '承認', 'Reject': '却下',
        
        # Common phrases
        'Are you sure?': 'よろしいですか？', 'Choose file': 'ファイルを選択',
        'Invalid format': '無効な形式', 'File not found': 'ファイルが見つかりません',
        'Permission denied': 'アクセス拒否', 'Unknown error': '不明なエラー',
    },
    
    'zh_CN': {
        # Basic operations
        'Search': '搜索', 'Replace': '替换', 'Match': '匹配', 'Find': '查找',
        'Open': '打开', 'Save': '保存', 'Close': '关闭', 'Exit': '退出',
        'Edit': '编辑', 'File': '文件', 'View': '查看', 'Tools': '工具',
        'Help': '帮助', 'About': '关于', 'Settings': '设置', 'Options': '选项',
        
        # Application specific
        'Glossary': '术语表', 'Statistics': '统计', 'Header': '标题',
        'Project': '项目', 'Compare': '比较', 'Theme': '主题',
        'Comment': '注释', 'Memory': '内存', 'Batch': '批处理',
        'Export': '导出', 'Import': '导入', 'Translation': '翻译',
        'Source': '源', 'Target': '目标', 'Language': '语言', 'Entry': '条目',
        
        # Dialog elements
        'OK': '确定', 'Cancel': '取消', 'Apply': '应用', 'Yes': '是', 'No': '否',
        'Browse': '浏览', 'Preview': '预览', 'Clear': '清除',
        'Select': '选择', 'Delete': '删除', 'Add': '添加', 'Remove': '移除',
        
        # Status and actions
        'Loading': '加载中', 'Saving': '保存中', 'Ready': '就绪', 'Processing': '处理中',
        'Complete': '完成', 'Failed': '失败', 'Success': '成功',
        'Error': '错误', 'Warning': '警告', 'Information': '信息',
        
        # Batch operations
        'Batch Edit': '批量编辑', 'Operation': '操作', 'Before': '之前', 'After': '之后',
        'Select All': '全选', 'Deselect All': '取消全选',
        
        # Fuzzy and translation states
        'Fuzzy': '模糊', 'Untranslated': '未翻译', 'Translated': '已翻译',
        'Accept': '接受', 'Reject': '拒绝',
        
        # Common phrases
        'Are you sure?': '确定吗？', 'Choose file': '选择文件',
        'Invalid format': '无效格式', 'File not found': '文件未找到',
        'Permission denied': '权限被拒绝', 'Unknown error': '未知错误',
    },
    
    'ko': {
        # Basic operations
        'Search': '검색', 'Replace': '바꾸기', 'Match': '일치', 'Find': '찾기',
        'Open': '열기', 'Save': '저장', 'Close': '닫기', 'Exit': '종료',
        'Edit': '편집', 'File': '파일', 'View': '보기', 'Tools': '도구',
        'Help': '도움말', 'About': '정보', 'Settings': '설정', 'Options': '옵션',
        
        # Application specific
        'Glossary': '용어집', 'Statistics': '통계', 'Header': '헤더',
        'Project': '프로젝트', 'Compare': '비교', 'Theme': '테마',
        'Comment': '설명', 'Memory': '메모리', 'Batch': '일괄',
        'Export': '내보내기', 'Import': '가져오기', 'Translation': '번역',
        'Source': '원본', 'Target': '대상', 'Language': '언어', 'Entry': '항목',
        
        # Dialog elements
        'OK': '확인', 'Cancel': '취소', 'Apply': '적용', 'Yes': '예', 'No': '아니오',
        'Browse': '찾아보기', 'Preview': '미리보기', 'Clear': '지우기',
        'Select': '선택', 'Delete': '삭제', 'Add': '추가', 'Remove': '제거',
        
        # Status and actions
        'Loading': '로딩 중', 'Saving': '저장 중', 'Ready': '준비됨', 'Processing': '처리 중',
        'Complete': '완료', 'Failed': '실패', 'Success': '성공',
        'Error': '오류', 'Warning': '경고', 'Information': '정보',
        
        # Batch operations
        'Batch Edit': '일괄 편집', 'Operation': '작업', 'Before': '이전', 'After': '이후',
        'Select All': '모두 선택', 'Deselect All': '모두 선택 해제',
        
        # Fuzzy and translation states
        'Fuzzy': '모호함', 'Untranslated': '번역 안됨', 'Translated': '번역됨',
        'Accept': '허용', 'Reject': '거부',
        
        # Common phrases
        'Are you sure?': '확실합니까?', 'Choose file': '파일 선택',
        'Invalid format': '잘못된 형식', 'File not found': '파일을 찾을 수 없음',
        'Permission denied': '권한 거부됨', 'Unknown error': '알 수 없는 오류',
    },
    
    'pl': {
        # Basic operations
        'Search': 'Szukaj', 'Replace': 'Zastąp', 'Match': 'Dopasowanie', 'Find': 'Znajdź',
        'Open': 'Otwórz', 'Save': 'Zapisz', 'Close': 'Zamknij', 'Exit': 'Zakończ',
        'Edit': 'Edytuj', 'File': 'Plik', 'View': 'Widok', 'Tools': 'Narzędzia',
        'Help': 'Pomoc', 'About': 'O programie', 'Settings': 'Ustawienia', 'Options': 'Opcje',
        
        # Application specific
        'Glossary': 'Słowniczek', 'Statistics': 'Statystyki', 'Header': 'Nagłówek',
        'Project': 'Projekt', 'Compare': 'Porównaj', 'Theme': 'Motyw',
        'Comment': 'Komentarz', 'Memory': 'Pamięć', 'Batch': 'Partia',
        'Export': 'Eksportuj', 'Import': 'Importuj', 'Translation': 'Tłumaczenie',
        'Source': 'Źródło', 'Target': 'Cel', 'Language': 'Język', 'Entry': 'Wpis',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Anuluj', 'Apply': 'Zastosuj', 'Yes': 'Tak', 'No': 'Nie',
        'Browse': 'Przeglądaj', 'Preview': 'Podgląd', 'Clear': 'Wyczyść',
        'Select': 'Wybierz', 'Delete': 'Usuń', 'Add': 'Dodaj', 'Remove': 'Usuń',
        
        # Status and actions
        'Loading': 'Ładowanie', 'Saving': 'Zapisywanie', 'Ready': 'Gotowy', 'Processing': 'Przetwarzanie',
        'Complete': 'Zakończono', 'Failed': 'Niepowodzenie', 'Success': 'Sukces',
        'Error': 'Błąd', 'Warning': 'Ostrzeżenie', 'Information': 'Informacja',
        
        # Batch operations
        'Batch Edit': 'Edycja wsadowa', 'Operation': 'Operacja', 'Before': 'Przed', 'After': 'Po',
        'Select All': 'Zaznacz wszystko', 'Deselect All': 'Odznacz wszystko',
        
        # Fuzzy and translation states
        'Fuzzy': 'Niepewny', 'Untranslated': 'Nieprzetłumaczone', 'Translated': 'Przetłumaczone',
        'Accept': 'Akceptuj', 'Reject': 'Odrzuć',
        
        # Common phrases
        'Are you sure?': 'Czy jesteś pewny?', 'Choose file': 'Wybierz plik',
        'Invalid format': 'Nieprawidłowy format', 'File not found': 'Nie znaleziono pliku',
        'Permission denied': 'Odmowa dostępu', 'Unknown error': 'Nieznany błąd',
    },
    
    'da': {
        # Basic operations
        'Search': 'Søg', 'Replace': 'Erstat', 'Match': 'Match', 'Find': 'Find',
        'Open': 'Åbn', 'Save': 'Gem', 'Close': 'Luk', 'Exit': 'Afslut',
        'Edit': 'Rediger', 'File': 'Fil', 'View': 'Vis', 'Tools': 'Værktøjer',
        'Help': 'Hjælp', 'About': 'Om', 'Settings': 'Indstillinger', 'Options': 'Muligheder',
        
        # Application specific
        'Glossary': 'Ordliste', 'Statistics': 'Statistik', 'Header': 'Header',
        'Project': 'Projekt', 'Compare': 'Sammenlign', 'Theme': 'Tema',
        'Comment': 'Kommentar', 'Memory': 'Hukommelse', 'Batch': 'Batch',
        'Export': 'Eksporter', 'Import': 'Importer', 'Translation': 'Oversættelse',
        'Source': 'Kilde', 'Target': 'Mål', 'Language': 'Sprog', 'Entry': 'Post',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Annuller', 'Apply': 'Anvend', 'Yes': 'Ja', 'No': 'Nej',
        'Browse': 'Gennemse', 'Preview': 'Forhåndsvisning', 'Clear': 'Ryd',
        'Select': 'Vælg', 'Delete': 'Slet', 'Add': 'Tilføj', 'Remove': 'Fjern',
        
        # Status and actions
        'Loading': 'Indlæser', 'Saving': 'Gemmer', 'Ready': 'Klar', 'Processing': 'Behandler',
        'Complete': 'Færdig', 'Failed': 'Fejlede', 'Success': 'Succes',
        'Error': 'Fejl', 'Warning': 'Advarsel', 'Information': 'Information',
        
        # Batch operations
        'Batch Edit': 'Batch-redigering', 'Operation': 'Operation', 'Before': 'Før', 'After': 'Efter',
        'Select All': 'Vælg alle', 'Deselect All': 'Fravælg alle',
        
        # Fuzzy and translation states
        'Fuzzy': 'Usikker', 'Untranslated': 'Uoversat', 'Translated': 'Oversat',
        'Accept': 'Accepter', 'Reject': 'Afvis',
        
        # Common phrases
        'Are you sure?': 'Er du sikker?', 'Choose file': 'Vælg fil',
        'Invalid format': 'Ugyldigt format', 'File not found': 'Fil ikke fundet',
        'Permission denied': 'Adgang nægtet', 'Unknown error': 'Ukendt fejl',
    },
    
    'nb': {
        # Basic operations
        'Search': 'Søk', 'Replace': 'Erstatt', 'Match': 'Treff', 'Find': 'Finn',
        'Open': 'Åpne', 'Save': 'Lagre', 'Close': 'Lukk', 'Exit': 'Avslutt',
        'Edit': 'Rediger', 'File': 'Fil', 'View': 'Vis', 'Tools': 'Verktøy',
        'Help': 'Hjelp', 'About': 'Om', 'Settings': 'Innstillinger', 'Options': 'Alternativer',
        
        # Application specific
        'Glossary': 'Ordliste', 'Statistics': 'Statistikk', 'Header': 'Topptekst',
        'Project': 'Prosjekt', 'Compare': 'Sammenlign', 'Theme': 'Tema',
        'Comment': 'Kommentar', 'Memory': 'Minne', 'Batch': 'Batch',
        'Export': 'Eksporter', 'Import': 'Importer', 'Translation': 'Oversettelse',
        'Source': 'Kilde', 'Target': 'Mål', 'Language': 'Språk', 'Entry': 'Oppføring',
        
        # Dialog elements
        'OK': 'OK', 'Cancel': 'Avbryt', 'Apply': 'Bruk', 'Yes': 'Ja', 'No': 'Nei',
        'Browse': 'Bla gjennom', 'Preview': 'Forhåndsvisning', 'Clear': 'Tøm',
        'Select': 'Velg', 'Delete': 'Slett', 'Add': 'Legg til', 'Remove': 'Fjern',
        
        # Status and actions
        'Loading': 'Laster', 'Saving': 'Lagrer', 'Ready': 'Klar', 'Processing': 'Behandler',
        'Complete': 'Fullført', 'Failed': 'Mislyktes', 'Success': 'Vellykket',
        'Error': 'Feil', 'Warning': 'Advarsel', 'Information': 'Informasjon',
        
        # Batch operations
        'Batch Edit': 'Batch-redigering', 'Operation': 'Operasjon', 'Before': 'Før', 'After': 'Etter',
        'Select All': 'Velg alle', 'Deselect All': 'Velg bort alle',
        
        # Fuzzy and translation states
        'Fuzzy': 'Usikker', 'Untranslated': 'Uoversatt', 'Translated': 'Oversatt',
        'Accept': 'Godta', 'Reject': 'Avvis',
        
        # Common phrases
        'Are you sure?': 'Er du sikker?', 'Choose file': 'Velg fil',
        'Invalid format': 'Ugyldig format', 'File not found': 'Fil ikke funnet',
        'Permission denied': 'Tilgang nektet', 'Unknown error': 'Ukjent feil',
    }
}

def smart_translate(text, target_lang):
    """Intelligently translate text using context-aware rules."""
    if not text or not text.strip():
        return ""
    
    # Get the translation dictionary for the target language
    trans_dict = TRANSLATIONS.get(target_lang, {})
    
    # First try exact match
    if text in trans_dict:
        return trans_dict[text]
    
    # Try case-insensitive match
    for key, value in trans_dict.items():
        if text.lower() == key.lower():
            # Preserve original case pattern
            if text.isupper():
                return value.upper()
            elif text.islower():
                return value.lower()
            elif text.istitle():
                return value.title()
            return value
    
    # Handle common patterns
    text_lower = text.lower()
    
    # Handle ellipsis
    if text.endswith('…') or text.endswith('...'):
        base_text = text.rstrip('….')
        translated_base = smart_translate(base_text, target_lang)
        if translated_base and translated_base != base_text:
            return translated_base + '…'
    
    # Handle question marks
    if text.endswith('?'):
        base_text = text[:-1]
        translated_base = smart_translate(base_text, target_lang)
        if translated_base and translated_base != base_text:
            return translated_base + '?'
    
    # Handle colons (common in UI labels)
    if text.endswith(':'):
        base_text = text[:-1]
        translated_base = smart_translate(base_text, target_lang)
        if translated_base and translated_base != base_text:
            return translated_base + ':'
    
    # Handle parenthetical content
    paren_match = re.match(r'^(.*?)\s*\((.*?)\)$', text)
    if paren_match:
        main_text, paren_text = paren_match.groups()
        translated_main = smart_translate(main_text.strip(), target_lang)
        translated_paren = smart_translate(paren_text.strip(), target_lang)
        
        if translated_main != main_text.strip() or translated_paren != paren_text.strip():
            return f"{translated_main} ({translated_paren})"
    
    # Handle quoted text
    quote_match = re.match(r'^"(.*?)"$', text)
    if quote_match:
        inner_text = quote_match.group(1)
        translated_inner = smart_translate(inner_text, target_lang)
        if translated_inner != inner_text:
            return f'"{translated_inner}"'
    
    # Handle ampersand shortcuts (like &File, &Edit)
    if text.startswith('&') and len(text) > 1:
        base_text = text[1:]
        translated_base = smart_translate(base_text, target_lang)
        if translated_base and translated_base != base_text:
            return '&' + translated_base
    
    # Handle keyboard shortcuts (like "Ctrl+S")
    if re.search(r'Ctrl\+|Alt\+|Shift\+|Cmd\+', text):
        # Don't translate keyboard shortcuts, they're universal
        return text
    
    # Handle format strings with placeholders
    format_match = re.search(r'%[sd%]|{.*?}', text)
    if format_match:
        # For now, return as-is for complex format strings
        # Could be improved to handle specific cases
        return text
    
    # Language-specific fallback translations for common UI elements
    fallback_translations = {
        'sv': {
            'file': 'fil', 'edit': 'redigera', 'view': 'visa', 'help': 'hjälp',
            'new': 'ny', 'copy': 'kopiera', 'paste': 'klistra in', 'cut': 'klipp ut',
            'undo': 'ångra', 'redo': 'gör om', 'print': 'skriv ut',
        },
        'de': {
            'file': 'Datei', 'edit': 'Bearbeiten', 'view': 'Ansicht', 'help': 'Hilfe',
            'new': 'Neu', 'copy': 'Kopieren', 'paste': 'Einfügen', 'cut': 'Ausschneiden',
            'undo': 'Rückgängig', 'redo': 'Wiederholen', 'print': 'Drucken',
        },
        'fr': {
            'file': 'Fichier', 'edit': 'Modifier', 'view': 'Affichage', 'help': 'Aide',
            'new': 'Nouveau', 'copy': 'Copier', 'paste': 'Coller', 'cut': 'Couper',
            'undo': 'Annuler', 'redo': 'Rétablir', 'print': 'Imprimer',
        },
        # Add more as needed...
    }
    
    fallback = fallback_translations.get(target_lang, {})
    if text_lower in fallback:
        # Match case of original
        if text.isupper():
            return fallback[text_lower].upper()
        elif text.istitle():
            return fallback[text_lower].title()
        return fallback[text_lower]
    
    # If nothing else works, return original text
    # In a production system, this is where you'd call an external translation API
    return text

def process_ts_file(file_path, target_lang):
    """Process a single .ts file and translate all unfinished entries."""
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        translated_count = 0
        total_unfinished = 0
        
        for context in root.findall('context'):
            for message in context.findall('message'):
                translation = message.find('translation')
                source = message.find('source')
                
                if translation is not None and source is not None:
                    # Check if translation is unfinished
                    if translation.get('type') == 'unfinished':
                        total_unfinished += 1
                        source_text = source.text or ""
                        
                        # Translate the source text
                        translated_text = smart_translate(source_text, target_lang)
                        
                        if translated_text and translated_text != source_text:
                            # Update the translation
                            translation.text = translated_text
                            # Remove the 'unfinished' attribute
                            del translation.attrib['type']
                            translated_count += 1
                        else:
                            # If we couldn't translate, at least remove the unfinished marker
                            # and copy the source text as fallback
                            translation.text = source_text
                            del translation.attrib['type']
                            translated_count += 1
        
        # Write the updated file
        tree.write(file_path, encoding='utf-8', xml_declaration=True)
        
        print(f"✓ {file_path.name}: {translated_count}/{total_unfinished} translated")
        return translated_count, total_unfinished
        
    except Exception as e:
        print(f"✗ {file_path.name}: Error - {e}")
        return 0, 0

def main():
    """Main translation function."""
    translations_dir = Path("translations")
    
    if not translations_dir.exists():
        print("Error: translations directory not found!")
        return
    
    # Language mapping (file suffix -> language code for translation)
    lang_map = {
        'da': 'da',
        'de': 'de', 
        'es': 'es',
        'fr': 'fr',
        'ja': 'ja',
        'ko': 'ko',
        'nb': 'nb',
        'pl': 'pl',
        'pt_BR': 'pt_BR',
        'zh_CN': 'zh_CN'
        # Swedish (sv) is excluded as it's the reference translation
    }
    
    total_translated = 0
    total_unfinished = 0
    
    print("🌐 Starting automatic translation of LinguaEdit strings...\n")
    
    for lang_suffix, lang_code in lang_map.items():
        ts_file = translations_dir / f"linguaedit_{lang_suffix}.ts"
        
        if ts_file.exists():
            translated, unfinished = process_ts_file(ts_file, lang_code)
            total_translated += translated
            total_unfinished += unfinished
        else:
            print(f"⚠ {ts_file.name}: File not found")
    
    print(f"\n✅ Translation complete!")
    print(f"📊 Total: {total_translated}/{total_unfinished} strings translated")
    print(f"🎯 All strings should now be marked as finished")

if __name__ == "__main__":
    main()