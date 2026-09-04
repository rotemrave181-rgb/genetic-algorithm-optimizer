import random
import time
from Solver_Engine import load_excel_data, run_optimization, export_results

# 1. פונקציות עזר של האלגוריתם הגנטי- הסתברויות להורים
def _roulette_select(probs: list[float]) -> int: # מקבלת רשימה של הסתברויות 
    r = random.random()# מגריל מספר בין 0 ל1
    cumulative = 0.0
    for idx, prob in enumerate(probs):
        cumulative += prob 
        if r <= cumulative:  # בוחרת את ההורים לפי המספר שהגרלנו  
            return idx
    return len(probs) - 1

def _order_crossover(parent_a: list[int], parent_b: list[int]) -> list[int]: # פונקציית הכלאה של שני הורים ליצירת ילד
    n = len(parent_a)
    
    # 1. בחירת נקודת חיתוך אחת אקראית
    cut = random.randint(1, n - 1) 
    
    # 2. החלק הראשון נלקח מהורה א
    child = parent_a[:cut]
    inherited_set = set(child)
    
    # 3. שאר הג'ובים החסרים נלקחים מהורה ב' עפ"י הסדר בו הם מצויים
    for gene in parent_b:
        if gene not in inherited_set:
            child.append(gene)
            
    return child

def _swap_mutation(chromosome: list[int]) -> list[int]: # פונקציית יצירת המוטציות 
    mutated = chromosome[:] # נבחר שני מיקומים אקראים בסדר ונחליף ביניהם- לא נשאר במינימום מקומי
    if len(mutated) < 2: return mutated 
    pos_a, pos_b = random.sample(range(len(mutated)), 2)
    mutated[pos_a], mutated[pos_b] = mutated[pos_b], mutated[pos_a]
    return mutated

# הפונקציה הראשית 
def Run_GA(Input_File_Name: str, Output_File_Name: str):
    print("--- Starting Genetic Algorithm Engine ---")
    
    try:
        # טעינת נתונים
        jobs, job_order, ga_params = load_excel_data(Input_File_Name) 
        if not (10 <= len(jobs) <= 100):
            print(f"[CRITICAL ERROR] Number of jobs must be between 10 and 100. Received: {len(jobs)}")
            return
        
        pop_size = int(ga_params['pop_size'])
        n_elites = int(ga_params['n_elites'])
        mut_prob = float(ga_params['mut_prob'])
        time_limit = float(ga_params['time_limit'])

        #  בדיקות תקינות קלט 
        if pop_size < 20: # אם גודל האוכלוסיה קטנה מ20- נשים 20
            print("[System] Adjusting population size to minimum allowed (20).")
            pop_size = 20

        elif pop_size > 200: # אם גודל האוכלוסיה גדול מ200 נשים 200
            print("[System] Adjusting population size to maximum allowed (200).")
            pop_size = 200

        if pop_size % 2 != 0: # אם גודל האוכלוסיה לא זוגי- נוסיף אחד
            print("[System] Adjusting population size to be even.")
            pop_size += 1
         

        if n_elites % 2 != 0: # אם מס הפתרונות שעוברים מדור לדור לא זוגי נוריד אחד ונדאג שיהיה אי שלילי
            print("[System] Adjusting elites to be even.")
            n_elites = max(0, n_elites - 1)
            
        if n_elites > 0.1 * pop_size: # אם מס הפתרונות שעוברים מדור לדור גדול מ10 אחוז מהאוכלוסיה נתריע ונדאג שיהיה 10 אחוז, וזוגי 
            print("[System] Adjusting elites to not exceed 10% of population.")
            n_elites = int(0.1 * pop_size)
            if n_elites % 2 != 0: 
                n_elites -= 1

        print(f"Pop: {pop_size}, Elites: {n_elites}, Mut Prob: {mut_prob}, Time Limit: {time_limit}s")

        def _evaluate(chromosome: list[int]): # מקבלת את סדר הגובים ושולחת אותו לסולבר
            res, pen = run_optimization(jobs, chromosome)
            return res, pen

        # ── שלב 0 - הערכת הסדר המקורי ──
        _, original_penalty = _evaluate(job_order) 
        print(f"[Step 0] Original penalty: {original_penalty}")
        ga_start_time = time.time()

        # ── שלב 1 - אתחול אוכלוסייה ──
        population = []  # יוצרים אוכלוסיה ראשונית עי ערבוב אקראי של סדר הגובים המקורי
        for _ in range(pop_size):
            chromosome = job_order[:]
            random.shuffle(chromosome)
            population.append(chromosome)

        # ── שלב 2 - הערכת האוכלוסייה ההתחלתית ──
        fitness = [] # רשימה של הציונים 
        for chromo in population: # עובר על כל הכרומוזומים- מוסיף ציון לרשימת הציונים
            _, pen = _evaluate(chromo)
            fitness.append(pen)

        best_idx = int(min(range(pop_size), key=lambda i: fitness[i])) #שומר את הציון הכי נמוך באוכלוסיה כרגע
        best_chromosome = population[best_idx][:]
        best_penalty = fitness[best_idx]
        best_results, _ = _evaluate(best_chromosome)

        generation = 0 # אתחול משתנים למעקב
        last_printed_best = best_penalty
        generation_of_best = 0
        
        print("\nStarting evolution loop...")

        while True: 
            generation += 1 # מונה דורות

            # ── שלב 3: הסתברויות בחירה  ──
            ranked_indices = sorted(range(pop_size), key=lambda i: fitness[i])  #מיון מספרי האינדקסים לפי הציונים 
            rank_of = [0] * pop_size 
            for rank_position, idx in enumerate(ranked_indices):  # לולאה שעוברת על הרשימה הממוינת ונותנת לכל אינדקס את הדירוג שלו
                rank_of[idx] = rank_position + 1

            rank_sum = pop_size * (pop_size + 1) / 2 # מחשב סכום מיקומים אפשריים ומייצר עבור כל פתרון הסבתרות להיבחר
            selection_probs = [(pop_size - rank_of[i] + 1) / rank_sum for i in range(pop_size)] #חישוב ההסתברויות לפי שיטת ה-ranking.

            # ── שלב 4: העברת פתרונות כפי שהם לדור הבא ──
            elite_indices = []
            while len(elite_indices) < n_elites:
                chosen_idx = _roulette_select(selection_probs)
                # מוודאים שהאינדקס הספציפי הזה טרם נבחר לאליטיזם
                if chosen_idx not in elite_indices:
                    elite_indices.append(chosen_idx)

            new_population = [population[i][:] for i in elite_indices]
            new_fitness = [fitness[i] for i in elite_indices]

            # ── שלב 5: שילוב  ──
            while len(new_population) < pop_size:
                # הגרלת אינדקס עבור הורה א'
                idx_a = _roulette_select(selection_probs)
                
                # הגרלת אינדקס עבור הורה ב'
                idx_b = _roulette_select(selection_probs)
                
                # וידוא מוחלט שלא נבחר אותו אינדקס ספציפי פעמיים באותו זיווג
                while idx_a == idx_b:
                    idx_b = _roulette_select(selection_probs)
                
                # שליפת הכרומוזומים מתוך האוכלוסייה
                parent_a = population[idx_a]
                parent_b = population[idx_b]
                
                child_a = _order_crossover(parent_a, parent_b)  # ילד א - חלק ראשון מהורה א
                child_b = _order_crossover(parent_b, parent_a)  # ילד ב - חלק ראשון מהורה ב
                
                new_population.append(child_a)
                new_fitness.append(None)
                
                if len(new_population) < pop_size:  # בדיקה שלא נחרוג מגודל האוכלוסייה
                    new_population.append(child_b)
                    new_fitness.append(None)

            # ── שלב 6: הערכת דור חדש ──
            for i in range(n_elites, pop_size): # עובר על הילדים החדשים שנוצרו - מחשב ציון
                _, pen = _evaluate(new_population[i])
                new_fitness[i] = pen # מעדכן רשימה 
                if pen < best_penalty: # אם הקנס של הילד הכי טוב מכל הדורות אז נעדכן את הפתרון ונששמור את הנתונים שלו
                    best_penalty = pen 
                    best_chromosome = new_population[i][:]
                    best_results, _ = _evaluate(best_chromosome)
                    generation_of_best = generation

            population = new_population 
            fitness = new_fitness

            # ── שלב 7: מוטציה  ──
            for i in range(pop_size): # עובר על האוכלוסיה 
                if random.random() < mut_prob:# מגריל מספר שהוא סיכוי להיות מוטציה
                    mutated = _swap_mutation(population[i])   # נשלח לעשות מוטציה 
                    _, pen = _evaluate(mutated)
                    population[i] = mutated
                    fitness[i] = pen
                    
                    if pen < best_penalty: # בדיקה האם ערך הפתרון של המוטציה הכי טוב עד כה
                        best_penalty = pen
                        best_chromosome = mutated[:]
                        best_results, _ = _evaluate(best_chromosome)
                        generation_of_best = generation

            # ── הדפסה כל 5 דורות ──
            if generation % 5 == 0: 
                print(f"--- Generation {generation} ---")
                print(f"Best penalty so far: {best_penalty}")
                if best_penalty < last_printed_best: # אם הפתרון השתפר- נעדכן
                    print(f"*** The best solution has improved! New best found in generation {generation_of_best} ***")
                    last_printed_best = best_penalty

            # ── שלב 8: בדיקת זמנים ──
            actual_runtime = time.time() - ga_start_time 
            if actual_runtime >= time_limit:
                break # אם עברנו את הזמן נצא 

        print(f"\nEvolution complete! Generations: {generation}, Time: {round(actual_runtime, 2)}s")

        # ייצוא תוצאות
        try:
            print("Attempting to export results to Excel...")
            export_results( # שופך את הנתונים של הפתרון הכי טוב 
                jobs=jobs,
                job_order=best_chromosome,
                results=best_results,
                total_penalty=best_penalty,
                filename=Output_File_Name,
                original_penalty=original_penalty,
                num_generations=generation,
                run_time=round(actual_runtime, 2)
            )
            print(f"Successfully exported to {Output_File_Name}!")
        except Exception as export_error: # אם קרתה שגיאה נדפיס תיאור מדויק
            print(f"[CRITICAL ERROR] Failed during export_results: {export_error}")
            print("Please check if the Excel file is open or if the export arguments match the Solver Engine requirements.")

    except Exception as main_error: 
        print(f"[CRITICAL ERROR] The Genetic Algorithm crashed: {main_error}")