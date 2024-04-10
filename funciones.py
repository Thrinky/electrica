import random

class MatlabGrader:
    def __init__(self, texto, variables_help='', lista_variables='', lista_variables_no_deseadas='', q_random=100, palabra='Question', frase='Find the value of the variable', sig=4):
        self.texto = texto
        self.variables_help = variables_help
        self.lista_variables = lista_variables
        self.lista_variables_no_deseadas = lista_variables_no_deseadas
        self.q_random = q_random
        self.palabra = palabra
        self.frase = frase
        self.sig = sig

    def ordenar_lis_num(self, list_num):
        cont = 0
        while True:
            for i in range(1, len(list_num)):
                if list_num[i] < list_num[i - 1]:
                    list_num[i], list_num[i - 1] = list_num[i - 1], list_num[i]
                    cont += 1
            if cont == 0:
                break
            cont = 0
        return list_num

    def ordenar_lis_str_inv(self, lista):
        new_orden = list(set(self.ordenar_lis_num([len(i) for i in lista])))[::-1]
        lista_des = [i for i in lista]
        lista_ord = []
        for num_len_orden in new_orden:
            may_min = [[], []]
            for str_l in lista_des:
                if len(str_l) == num_len_orden:
                    if str_l[0].upper() == str_l[0]:
                        may_min[0].append(str_l)
                    else:
                        may_min[1].append(str_l)
            lista_ord += may_min[0] + may_min[1]
        return lista_ord

    def units_value(self, var_str):
        values_more_str = dict(zip('sol,Sol,phi,Phi,Delta,delta,f,Phase,phase,Eta,eta,ang,p,pp,s,w,N,E,V,I,Z,R,X,S,P,Q'.split(','), ',,deg,deg,,,Hz,deg,deg,,,deg,,,,rad/s,rpm,V,V,A,Ω,Ω,Ω,VA,W,VAr'.split(',')))
        ord_values_more_str = self.ordenar_lis_str_inv([i for i in values_more_str])
        for i, var_tab in enumerate(ord_values_more_str):
            len_var_tab = len(var_tab)
            len_var_str = len(var_str)
            if len_var_tab <= len(var_str):
                if (var_tab == var_str[:len_var_tab]) or (var_tab == var_str[len_var_str - len_var_tab:]):
                    unit = values_more_str[var_tab]
                    if unit == 'deg':
                        return unit, var_str
                    else:
                        if 'pu' in var_str:
                            unit = 'pu'
                            return unit, var_str
                        else:
                            return unit, var_str
                    break
        if i == len(ord_values_more_str) - 1:
            unit = ''
            return unit, var_str

    def dependent_variable(self, line):
        if ('=' not in line) or ('%' == line[0]):
            return '', False
        else:
            if '=' in line:
                line = line.split('%')[0]
                l = ''.join([i for i in (line.split('=')[0]).split(' ') if i != ''])
                r = ''.join([i for i in line.split('=')[1] if i != ';'])
                for i, car in enumerate(r):
                    if car == '^':
                        r = r[:i] + '**' + r[i + 1:]
                if ('(' in r) or ('[' in r):
                    cont_cor_open = 0
                    cor_open = []
                    cont_par_open = 0
                    par_open = []
                    for i, car in enumerate(r):
                        if car == '[':
                            cont_cor_open += 1
                            cor_open.append(i)
                        else:
                            if car == ']':
                                cont_cor_open -= 1
                                if sum([1 for k in r[cor_open[-1] + 1:i] if ' ' == k]) != 0:
                                    new_r = ''.join([',' if k == ' ' else k for k in r[cor_open[-1] + 1:i]])
                                    if cor_open[-1] == 0:
                                        r = r[0] + new_r + r[i:]
                                    else:
                                        r = r[:cor_open[-1] + 1] + new_r + r[i:]
                                cor_open.remove(cor_open[-1])
                            else:
                                if car == '(':
                                    cont_par_open += 1
                                    par_open.append(i)
                                else:
                                    if car == ')':
                                        cont_par_open -= 1
                                        if sum([1 for k in r[par_open[-1] + 1:i] if ' ' == k]) != 0:
                                            new_r = ''.join([',' if k == ' ' else k for k in r[par_open[-1] + 1:i]])
                                            if par_open[-1] == 0:
                                                r = r[0] + new_r + r[i:]
                                            else:
                                                r = r[:par_open[-1] + 1] + new_r + r[i:]
                                        par_open.remove(par_open[-1])
                try:
                    (eval(r))
                    value = False
                except:
                    value = True
                return l, value

    def frases(self, i, unit, var_str, palabra, frase, sig=4):
        if unit == 'pu':
            fq = f'\033[1m{palabra} {i + 1})\033[0m\n{frase} ({var_str})\n'
            f_sol = f"""{frase} ({var_str})
{var_str}_Reference=round(referenceVariables.{var_str},{sig},'significant');
assessVariableEqual('{var_str}', {var_str}_Reference);

"""
        else:
            if unit == '':
                fq = f'\033[1m{palabra} {i + 1})\033[0m\n{frase} ({var_str})\n'
                f_sol = f"""{frase} ({var_str})
{var_str}_Reference=round(referenceVariables.{var_str},{sig},'significant');
assessVariableEqual('{var_str}', {var_str}_Reference);

"""
            else:
                fq = f'\033[1m{palabra} {i + 1})\033[0m\n{frase} [{unit}] ({var_str})\n'
                f_sol = f"""{frase} [{unit}] ({var_str})
{var_str}_Reference=round(referenceVariables.{var_str},{sig},'significant');
assessVariableEqual('{var_str}', {var_str}_Reference);

"""
        return fq, f_sol

    def matlab_grader_all(self):
        texto = self.texto
        variables_help = self.variables_help
        lista_variables = self.lista_variables
        lista_variables_no_deseadas = self.lista_variables_no_deseadas
        q_random = self.q_random
        palabra = self.palabra
        frase = self.frase
        sig = self.sig

        q_random = abs(q_random)
        frase_cuestiones = []
        frases_sol = []
        variables = []
        posi = []
        if '=' in texto:
            text_line = texto.split('\n')
            if text_line[0] == '':
                text_line = text_line[1:]
            if text_line[-1] == '':
                text_line = text_line[:-1]
            text_line = [i for i in text_line if ((frase in i) or (palabra in i)) == False]
            estudiante = [i for i in text_line]
            for pos, txt in enumerate(text_line):
                line = txt
                var, value = self.dependent_variable(line)
                if value:
                    variables.append(var)
                    posi.append(pos)
            print(5 * 20 * '-'+'\nAll Variables\n' + ','.join(variables) + '\n' + 5 * 20 * '-')
            if variables_help != '':
                variables_help = (''.join([i for i in variables_help if ' ' != i])).split(',')
                variables_help = [i for i in variables_help if '' != i]
                var_h_def = []
                for var_h in variables_help:
                    for i in range(len(variables)):
                        if var_h == variables[i]:
                            var_h_def.append(var_h)
                            variables.remove(var_h)
                            posi.remove(posi[i])
                            break
                print('Help Variables\n' + ','.join(var_h_def) + '\n' + 5 * 20 * '-')
            for i in posi:
                estudiante[i] = ''
            new_var = [i for i in variables]
            print('Variables\n' + ','.join(variables) + '\n' + 5 * 20 * '-')
            if lista_variables_no_deseadas != '':
                lista_variables_no_deseadas = (''.join([i for i in lista_variables_no_deseadas if ' ' != i])).split(',')
                lista_variables_no_deseadas = [i for i in lista_variables_no_deseadas if '' != i]
                new_var_n_d = []
                for var_n_d in lista_variables_no_deseadas:
                    for i in range(len(new_var)):
                        if var_n_d == new_var[i]:
                            new_var_n_d.append(var_n_d)
                            new_var.remove(var_n_d)
                            break
                print('Unwanted Variable\n' + ','.join(new_var_n_d) + '\n' + 5 * 20 * '-')
                print('variables without unwanted variables\n' + ','.join(new_var) + '\n' + 5 * 20 * '-')

            if lista_variables != '':
                lista_variables = (''.join([i for i in lista_variables if ' ' != i])).split(',')
                lista_variables = [i for i in lista_variables if '' != i]
                elim_l = []
                for var_l in lista_variables:
                    if (var_l in new_var) == False:
                        elim_l.append(var_l)
                [lista_variables.remove(i) for i in elim_l]

                variables_random = lista_variables
                if variables_random == []:
                    variables_random = new_var
                print('Variables Choisies\n' + ','.join(variables_random) + '\n' + 5 * 20 * '-')
            else:
                if q_random == 100:
                    variables_random = [i for i in new_var]
                else:
                    if 100 < q_random:
                        variables_random = [i for i in new_var]
                    else:
                        n_random = int(q_random / 100 * len(new_var))
                        variables_random = sorted(random.sample(new_var, n_random), key=lambda x: new_var.index(x))
                        print('Random Variables\n' + ','.join(variables_random) + '\n' + 5 * 20 * '-')
            for i, var in enumerate(variables_random):
                for j, var_1 in enumerate(variables):
                    if var_1 == var:
                        pos_f = posi[j]
                        break

                unit, var_str = self.units_value(var)
                fq, f_sol = self.frases(i=i, unit=unit, var_str=var_str, palabra=palabra, frase=frase)
                new_text = fq.split('\n')
                text_line[pos_f] = '\n'.join(new_text) + text_line[pos_f]
                estudiante[pos_f] = '\n'.join(new_text)
                frase_cuestiones.append(fq)
                frases_sol.append(f_sol)

            print('Problem Questions [Letter format in word = Helvetica] (Text)\n' + 5 * 20 * '-')
            print(''.join(frase_cuestiones))
            print('\n')
            print(5 * 20 * '-' + '\n' + 'Reference Code (Matlab)\n' + 5 * 20 * '-')
            print('\n'.join(text_line))
            print('\n')
            print(5 * 20 * '-' + '\n' + 'Student Code (Matlab)\n' + 5 * 20 * '-')
            print('\n'.join(estudiante))
            print('\n')
            print(5 * 20 * '-' + '\n' + 'Correction Code (Matlab)\n' + 5 * 20 * '-')
            print(''.join(frases_sol))
        else:
            texto = ''.join([i for i in texto if i != ' '])
            if texto[0] == '':
                texto = texto[1:]
            if texto[-1] == '':
                texto = texto[:-1]
            texto = ''.join([i for i in texto if i != '\n'])
            variables = texto.split(',')
            variables_random = variables
            for i, var in enumerate(variables_random):
                unit, var_str = self.units_value(var)
                fq, f_sol = self.frases(i=i, unit=unit, var_str=var_str, palabra=self.palabra, frase=self.frase)
                frase_cuestiones.append(fq)
                frases_sol.append(f_sol)
            print(5 * 20 * '-' + '\n' + 'Problem Questions [Letter format in word = Helvetica] (Text)\n' + 5 * 20 * '-')
            print(''.join(frase_cuestiones))
            print(5 * 20 * '-' + '\n' + 'Problem questions (Matlab)\n' + 5 * 20 * '-')
            print(''.join(frases_sol))

