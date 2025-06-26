import csv
import re
from datetime import datetime
from llama_cpp import Llama

class TranscriptProcessor:
    def __init__(self):
        # Inicializar el modelo LLM
        self.llm = Llama(
            model_path="./models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
            n_ctx=2048
        )
        
        # Diccionario de correcciones comunes
        self.common_corrections = {
            r'vaquen': 'Backend',
            r'\bcua\b': 'QA',
            r'\bemvipi\b': 'MVP',
            r'\bmvp\b': 'MVP (Mínimo Producto Viable)',
            r'\bfronen\b': 'Frontend',
            r'\bdiseño uxi\b': 'Diseño UX/UI',
            r'\bdevops\b': 'DevOps',
            r'\bscrum\b': 'Scrum',
            r'\bkanban\b': 'Kanban',
            r'\bpo\b': 'Product Owner',
            r'\bsm\b': 'Scrum Master'
        }
        
        # Categorías de tareas predefinidas
        self.task_categories = [
            'Desarrollo', 'Diseño', 'Testing', 'Revisión', 
            'Documentación', 'Reunión', 'Planificación', 
            'Seguimiento', 'Feedback', 'Decisión', 'Problema'
        ]
    
    def load_transcript(self, file_path):
        """Cargar el archivo de transcripción"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    
    def preprocess_transcript(self, transcript):
        """Preprocesar la transcripción para corregir errores comunes"""
        for error, correction in self.common_corrections.items():
            transcript = re.sub(error, correction, transcript, flags=re.IGNORECASE)
        return transcript
    
    def generate_prompt(self, transcript):
        """Generar el prompt para el LLM"""
        prompt = f"""
        Analiza la siguiente transcripción de una reunión laboral y extrae la información relevante.
        La transcripción puede contener errores de escritura o palabras mal transcritas.

        INSTRUCCIONES DETALLADAS:
        1. PERSONAS:
           - Identifica todos los nombres de personas mencionadas
           - Corrige posibles errores en los nombres basándote en el contexto

        2. TAREAS:
           - Extrae todas las tareas asignadas con: responsable, deadline y descripción clara
           - Clasifica cada tarea en una de estas categorías: {', '.join(self.task_categories)}
           - Para tareas técnicas, especifica tecnología/lenguaje si se menciona (ej: "API en Node.js")

        3. FECHAS:
           - Extrae todas las fechas importantes (deadlines, reuniones, entregables)
           - Normaliza el formato a DD/MM/YYYY

        4. ERRORES Y CORRECCIONES:
           - Detecta posibles errores de transcripción (palabras que no coincidan con términos técnicos o nombres conocidos)
           - Para cada error, proporciona 2-3 sugerencias de lo que podría ser la palabra correcta
           - Incluye una confianza del 1-5 en cada corrección (1=baja, 5=alta)

        5. PUNTOS CLAVE:
           - Extrae decisiones importantes tomadas
           - Identifica problemas mencionados y su posible solución
           - Extrae feedback dado a personas o equipos
           - Identifica dependencias entre tareas

        FORMATO DE SALIDA PARA EL RESUMEN:
        - RESUMEN: [resumen conciso de los puntos principales en bullet points]
        - ERRORES_DETECTADOS: [lista de posibles errores con formato: "error original|sugerencia1(confianza)|sugerencia2(confianza)|..."]
        - PERSONAS: [lista de nombres identificados y corregidos]
        - FECHAS: [lista de fechas importantes normalizadas]
        
        FORMATO DE SALIDA PARA LA TABLA CSV (ejemplo):
        Tipo,Detalle,Responsable,Fecha,Comentarios/Correcciones,Dependencias,Tecnología

        TRANSCRIPCIÓN:
        {transcript}
        """
        return prompt
    
    def process_transcript(self, transcript):
        """Procesar la transcripción con el LLM"""
        # Preprocesar para corregir errores comunes
        transcript = self.preprocess_transcript(transcript)
        
        prompt = self.generate_prompt(transcript)
        output = self.llm(prompt, max_tokens=3000, echo=False)
        return output['choices'][0]['text']
    
    def parse_llm_output(self, output):
        """Parsear la salida del LLM para extraer información estructurada"""
        result = {
            'summary': '',
            'errors': [],
            'people': [],
            'dates': [],
            'tasks': [],
            'decisions': [],
            'problems': []
        }
        
        # Extraer secciones
        sections = re.split(r'\n- ', output)
        
        for section in sections:
            if section.startswith('RESUMEN:'):
                result['summary'] = section.replace('RESUMEN:', '').strip()
            elif section.startswith('ERRORES_DETECTADOS:'):
                errors = section.replace('ERRORES_DETECTADOS:', '').strip().split('\n')
                result['errors'] = [self.parse_error(e.strip()) for e in errors if e.strip()]
            elif section.startswith('PERSONAS:'):
                people = section.replace('PERSONAS:', '').strip().split(',')
                result['people'] = [p.strip() for p in people if p.strip()]
            elif section.startswith('FECHAS:'):
                dates = section.replace('FECHAS:', '').strip().split(',')
                result['dates'] = [self.normalize_date(d.strip()) for d in dates if d.strip()]
        
        # Extraer tareas de la parte de tabla CSV si existe
        csv_lines = []
        if 'Tipo,Detalle,Responsable,Fecha,Comentarios/Correcciones' in output:
            csv_part = output.split('Tipo,Detalle,Responsable,Fecha,Comentarios/Correcciones')[-1]
            csv_lines = [line.strip() for line in csv_part.split('\n') if line.strip() and ',' in line]
            
            for line in csv_lines:
                parts = line.split(',')
                if len(parts) >= 4:
                    task = {
                        'type': self.categorize_task(parts[0]),
                        'detail': parts[1],
                        'responsible': parts[2],
                        'date': self.normalize_date(parts[3]),
                        'comments': parts[4] if len(parts) > 4 else '',
                        'dependencies': parts[5] if len(parts) > 5 else '',
                        'technology': parts[6] if len(parts) > 6 else ''
                    }
                    result['tasks'].append(task)
        
        # Extraer decisiones y problemas del resumen
        self.extract_decisions_and_problems(result)
        
        return result
    
    def parse_error(self, error_str):
        """Parsear la información de error con múltiples sugerencias"""
        if '|' not in error_str:
            return {'original': error_str, 'suggestions': []}
        
        parts = error_str.split('|')
        original = parts[0].strip()
        suggestions = []
        
        for suggestion in parts[1:]:
            # Extraer confianza si está presente
            confidence = 3  # valor por defecto
            sug_text = suggestion
            if '(' in suggestion and ')' in suggestion:
                match = re.search(r'(.+?)\((\d)\)', suggestion)
                if match:
                    sug_text = match.group(1).strip()
                    confidence = int(match.group(2))
            
            suggestions.append({
                'text': sug_text,
                'confidence': confidence
            })
        
        return {
            'original': original,
            'suggestions': suggestions
        }
    
    def normalize_date(self, date_str):
        """Intentar normalizar fechas a formato DD/MM/YYYY"""
        if not date_str:
            return date_str
        
        # Intentar parsear fechas comunes
        date_formats = [
            '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
            '%Y/%m/%d', '%Y-%m-%d',
            '%d/%m/%y', '%d-%m-%y'
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%d/%m/%Y')
            except ValueError:
                continue
        
        return date_str
    
    def categorize_task(self, task_type):
        """Asignar categoría estándar a la tarea"""
        task_type = task_type.strip().capitalize()
        
        # Buscar coincidencia exacta
        if task_type in self.task_categories:
            return task_type
            
        # Buscar coincidencia parcial
        for category in self.task_categories:
            if category.lower() in task_type.lower():
                return category
        
        # Si no coincide, usar "Otros" o la primera palabra
        return task_type.split()[0] if task_type else 'Otros'
    
    def extract_decisions_and_problems(self, result):
        """Extraer decisiones y problemas del resumen"""
        if not result['summary']:
            return
        
        # Buscar patrones en el resumen
        lines = result['summary'].split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # Detectar decisiones
            if 'decidió' in line_lower or 'decisión' in line_lower or 'acordó' in line_lower:
                result['decisions'].append(line.strip('- ').strip())
            
            # Detectar problemas
            if 'problema' in line_lower or 'error' in line_lower or 'issue' in line_lower or 'bug' in line_lower:
                problem = {
                    'description': line.strip('- ').strip(),
                    'status': 'Identificado'  # por defecto
                }
                
                if 'solucionado' in line_lower or 'resuelto' in line_lower:
                    problem['status'] = 'Resuelto'
                elif 'en progreso' in line_lower:
                    problem['status'] = 'En progreso'
                
                result['problems'].append(problem)
    
    def save_results(self, data, summary_path='output/resumen_reunion.txt', csv_path='output/detalles_reunion.csv'):
        """Guardar los resultados en archivos"""
        # Guardar resumen
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== RESUMEN DE LA REUNIÓN ===\n\n")
            f.write(data['summary'] + "\n\n")
            
            f.write("=== PERSONAS MENCIONADAS ===\n")
            f.write(", ".join(data['people']) + "\n\n")
            
            f.write("=== FECHAS IMPORTANTES ===\n")
            f.write(", ".join(data['dates']) + "\n\n")
            
            if data['errors']:
                f.write("=== POSIBLES ERRORES DE TRANSCRIPCIÓN ===\n")
                for error in data['errors']:
                    f.write(f"- Original: {error['original']}\n")
                    for sug in error['suggestions']:
                        f.write(f"  Sugerencia: {sug['text']} (Confianza: {sug['confidence']}/5)\n")
                    f.write("\n")
            
            if data['decisions']:
                f.write("\n=== DECISIONES IMPORTANTES ===\n")
                for decision in data['decisions']:
                    f.write(f"- {decision}\n")
            
            if data['problems']:
                f.write("\n=== PROBLEMAS IDENTIFICADOS ===\n")
                for problem in data['problems']:
                    f.write(f"- {problem['description']} [Estado: {problem['status']}]\n")
        
        # Guardar CSV con detalles
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'Tipo', 'Detalle', 'Responsable', 'Fecha', 
                'Comentarios/Correcciones', 'Dependencias', 'Tecnología'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for task in data['tasks']:
                writer.writerow({
                    'Tipo': task['type'],
                    'Detalle': task['detail'],
                    'Responsable': task['responsible'],
                    'Fecha': task['date'],
                    'Comentarios/Correcciones': task['comments'],
                    'Dependencias': task['dependencies'],
                    'Tecnología': task['technology']
                })

def main():
    processor = TranscriptProcessor()
    
    # Cargar transcripción
    transcript = processor.load_transcript('output/transcripcion.txt')
    
    # Procesar con LLM
    print("Procesando la transcripción con Mistral...")
    llm_output = processor.process_transcript(transcript)
    
    # Parsear resultados
    processed_data = processor.parse_llm_output(llm_output)
    
    # Guardar resultados
    processor.save_results(processed_data)
    
    print("Procesamiento completado. Resultados guardados en:")
    print("- output/resumen_reunion.txt")
    print("- output/detalles_reunion.csv")

if __name__ == "__main__":
    main()