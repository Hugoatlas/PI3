import export
import settings
import matplotlib.pyplot as plt
import cv2
import tkinter as tk
from PIL import ImageTk, Image
from tkinter.filedialog import askopenfilename
from analyseImage import preprocess, get_edges

global image_src, do_run_search

# Let's not talk about this mess of a gui


def open_window(image_src_list, settings_src):
    settings.do_run_search = False

    class Setting:
        def __init__(self, frame, name, def_val, lim, step, style):
            self.value = def_val
            self.limits = lim
            self.step = step
            self.frm = frame
            self.style = style
            if self.style == 'slider':
                self.value = float(self.value)
                self.lbl_name = tk.Label(master=self.frm, text=name)
                self.scale = tk.Scale(master=self.frm, from_=self.limits[0], to=self.limits[1],
                                      orient=tk.HORIZONTAL, command=self.val, resolution=self.step, digits=3,
                                      tickinterval=0, length=100, sliderlength=20,
                                      showvalue=False, troughcolor='gray')
                self.scale.set(self.value)
                self.lbl_value = tk.Label(master=self.frm, text=f'{self.scale.get()}')
            elif self.style == 'check_box':
                self.value = bool(self.value)
                self.boolVar = tk.BooleanVar()
                self.check_box = tk.Checkbutton(master=self.frm, text=name, variable=self.boolVar, command=self.update)
            elif self.style == 'buttons':
                self.value = int(self.value)
                self.lbl_name = tk.Label(master=self.frm, text=name)
                self.btn_decrease = tk.Button(master=self.frm, text='-', command=self.decrease)
                self.btn_increase = tk.Button(master=self.frm, text='+', command=self.increase)
                self.lbl_value = tk.Label(master=self.frm, text=f'{self.value}')
            else:
                self.lbl_name = tk.Label(master=self.frm, text=name)
                self.lbl_value = tk.Entry(master=self.frm, justify='left', textvariable=self.value)
                self.lbl_value.insert(0, self.value)

        def update_checkbox(self):
            self.value = self.boolVar.get()

        def update(self):
            if self.style == 'slider':
                self.value = float(self.lbl_value['text'])
                self.scale.set(self.value)
                self.scale['digits'] = 3
                self.lbl_value['text'] = f'{self.scale.get()}'
            elif self.style == 'check_box':
                self.value = self.boolVar.get()
            elif self.style == 'buttons':
                self.value = int(self.lbl_value['text'])
            else:
                self.value = int(self.lbl_value.get())

        def retrieve(self):
            if self.style == 'slider':
                self.lbl_value['text'] = f'{self.value}'
                self.scale.set(self.value)
                self.scale['digits'] = 3
                self.lbl_value['text'] = f'{self.scale.get()}'
            elif self.style == 'check_box':
                self.boolVar.set(bool(self.value))
            elif self.style == 'buttons':
                self.lbl_value['text'] = f'{self.value}'
            else:
                self.lbl_value.delete(0, 'end')
                self.lbl_value.insert(0, f'{self.value}')

        def val(self, value):
            self.value = value
            self.lbl_value['text'] = f'{self.value}'

        def increase(self):
            value = int(self.lbl_value['text'])
            value += self.step
            self.value = min(max(value, self.limits[0]), self.limits[1])
            self.lbl_value['text'] = f'{self.value}'

        def decrease(self):
            value = int(self.lbl_value['text'])
            value -= self.step
            self.value = min(max(value, self.limits[0]), self.limits[1])
            self.lbl_value['text'] = f'{self.value}'

        def set_in_frame(self, row, col):
            if self.style == 'slider':
                self.lbl_name.grid(row=row, column=col, sticky='nsew', padx=5)
                self.scale.grid(row=row, column=col + 1, sticky='nsew', padx=5)
                self.lbl_value.grid(row=row, column=col + 2, padx=5)
            elif self.style == 'check_box':
                self.check_box.grid(row=row, column=col + 1, sticky='nsew', padx=5, pady=5)
            elif self.style == 'buttons':
                self.lbl_name.grid(row=row, column=col, sticky='nsew', padx=5)
                self.btn_decrease.grid(row=row, column=col + 1, sticky='nsew', padx=5, pady=5)
                self.lbl_value.grid(row=row, column=col + 2, padx=5, pady=5)
                self.btn_increase.grid(row=row, column=col + 3, sticky='nsew', padx=5, pady=5)
            else:
                self.lbl_name.grid(row=row, column=col, sticky='nsew', padx=5)
                self.lbl_value.grid(row=row, column=col + 1, padx=5)

    def update_setting(setting_list):
        for i in range(0, len(setting_list)):
            setting_list[i].update()

    def retrieve_setting(setting_list):
        for i in range(0, len(setting_list)):
            setting_list[i].retrieve()

    def open_file():
        global image_src
        filepath = askopenfilename(
            filetypes=[('Image Files', '*.jpg'), ('All Files', '*.*')]
        )
        if not filepath:
            return
        image_src = filepath
        image_bgr = cv2.imread(image_src)
        cv2.imwrite('write.jpg', image_bgr)
        image = Image.open('write.jpg')
        resized_image = fit_image_to_canvas(image, canvas_image_0)
        canvas_image_0.image = ImageTk.PhotoImage(resized_image)
        canvas_image_0.create_image(0, 0, image=canvas_image_0.image, anchor='nw')
        window.title(f'Image Editor - {filepath}')

    def fit_image_to_canvas(image, canvas):
        basewidth = int(canvas['width'])
        baseheight = int(canvas['height'])
        if (basewidth / float(image.size[0])) < (baseheight / float(image.size[1])):
            wpercent = (basewidth / float(image.size[0]))
            hsize = int((float(image.size[1]) * float(wpercent)))
            resized_image = image.resize((basewidth, hsize), Image.ANTIALIAS)
        else:
            wpercent = (baseheight / float(image.size[1]))
            hsize = int((float(image.size[0]) * float(wpercent)))
            resized_image = image.resize((hsize, baseheight), Image.ANTIALIAS)
        return resized_image

    def start_search():
        settings.do_run_search = True
        window.destroy()

    def insert_search_settings_in_list(listbox, list_of_settings):
        for i in range(0, len(list_of_settings)):
            setting = list_of_settings[i]
            string = f'R = {setting.searched_radius}, Iterations = {setting.iterations}, ' \
                     f'Color difference = {setting.use_color_differences}'
            listbox.insert(i, string)

    def apply_changes(srch_stgs):
        update_setting(settings_list)
        srch_stgs.edges_para.gauss_1 = settings_list[0].value
        srch_stgs.edges_para.thresh1_1 = settings_list[1].value
        srch_stgs.edges_para.thresh2_1 = settings_list[2].value
        srch_stgs.edges_para.gauss_2 = settings_list[3].value
        srch_stgs.edges_para.thresh1_2 = settings_list[4].value
        srch_stgs.edges_para.thresh2_2 = settings_list[5].value
        srch_stgs.use_color_differences = settings_list[6].value
        srch_stgs.color_weights[0] = settings_list[7].value
        srch_stgs.color_weights[1] = settings_list[8].value
        srch_stgs.color_weights[2] = settings_list[9].value
        srch_stgs.match_para.max_dim = settings_list[10].value
        srch_stgs.searched_radius = settings_list[11].value
        srch_stgs.contour_para.nb_points = settings_list[12].value
        srch_stgs.iterations = settings_list[13].value
        return srch_stgs

    def apply_and_analyze():
        global image_src
        _ = apply_changes(search_settings)

        if 'image_src' in globals():
            image_bgr = cv2.imread(image_src)
            image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
            image, img, scale_factor = preprocess(image_rgb, search_settings)

            # Obtain edges map at full scale and rescaled
            edges = get_edges(image, search_settings.edges_para.gauss_1, search_settings.edges_para.thresh1_1,
                              search_settings.edges_para.thresh2_1)
            edg = get_edges(img, search_settings.edges_para.gauss_2, search_settings.edges_para.thresh1_2,
                            search_settings.edges_para.thresh2_2)

            display(image, 1)
            display(edges, 2)
            display(edg, 3)
            plt.show()

    def retrieve_settings(srch_stgs):
        settings_list[0].value = srch_stgs.edges_para.gauss_1
        settings_list[1].value = srch_stgs.edges_para.thresh1_1
        settings_list[2].value = srch_stgs.edges_para.thresh2_1
        settings_list[3].value = srch_stgs.edges_para.gauss_2
        settings_list[4].value = srch_stgs.edges_para.thresh1_2
        settings_list[5].value = srch_stgs.edges_para.thresh2_2
        settings_list[6].value = srch_stgs.use_color_differences
        settings_list[7].value = srch_stgs.color_weights[0]
        settings_list[8].value = srch_stgs.color_weights[1]
        settings_list[9].value = srch_stgs.color_weights[2]
        settings_list[10].value = srch_stgs.match_para.max_dim
        settings_list[11].value = srch_stgs.searched_radius
        settings_list[12].value = srch_stgs.contour_para.nb_points
        settings_list[12].value = srch_stgs.iterations
        retrieve_setting(settings_list)
        return settings_list

    def retrieve_settings_to_current():
        selected = search_listbox.curselection()
        srch_stgs = settings.Search(r=200, n=1, use_color_differences=False)
        if len(selected) != 0:
            for i in selected:
                srch_stgs = search_settings_list[i]
            _ = retrieve_settings(srch_stgs)

    def save_search_settings():
        srch_stgs = apply_changes(settings.Search(r=200, n=1, use_color_differences=False))
        selected = search_listbox.curselection()
        if len(selected) != 0:
            for i in selected:
                search_settings_list[i] = srch_stgs
        search_listbox.delete(0, 'end')
        insert_search_settings_in_list(search_listbox, search_settings_list)
        export.save_data(search_settings_list, settings_src)

    def remove_search_settings():
        selected = search_listbox.curselection()
        if len(selected) != 0:
            for i in reversed(selected):
                search_settings_list.pop(i)
        search_listbox.delete(0, 'end')
        insert_search_settings_in_list(search_listbox, search_settings_list)
        export.save_data(search_settings_list, settings_src)

    def add_search_settings():
        srch_stgs = apply_changes(settings.Search(r=200, n=1, use_color_differences=False))
        search_settings_list.append(srch_stgs)
        search_listbox.delete(0, 'end')
        insert_search_settings_in_list(search_listbox, search_settings_list)
        export.save_data(search_settings_list, settings_src)

    search_settings_list = export.open_data(settings_src)
    search_settings = settings.Search(r=200, n=1, use_color_differences=False)
    image_src = ''
    window = tk.Tk()
    window.title('Play with settings')

    window.rowconfigure(0, minsize=600, weight=1)
    window.columnconfigure(1, minsize=800, weight=1)

    frm_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)
    frm_image = tk.Frame(window, bd=2)
    frm_settings = tk.Frame(frm_buttons, relief=tk.RAISED, bd=2)
    frm_canny = tk.Frame(frm_settings, relief=tk.RAISED, bd=2)
    lbl_canny_1 = tk.Label(frm_canny, text='Regular image')
    lbl_canny_2 = tk.Label(frm_canny, text='Downsized image')
    frm_canny_1 = tk.Frame(frm_canny, relief=tk.RAISED, bd=2)
    frm_canny_2 = tk.Frame(frm_canny, relief=tk.RAISED, bd=2)
    frm_colors = tk.Frame(frm_settings, relief=tk.RAISED, bd=2)
    frm_search = tk.Frame(frm_settings, relief=tk.RAISED, bd=2)
    btn_open = tk.Button(frm_buttons, text='Open', command=open_file)
    btn_start_search = tk.Button(frm_buttons, text='Start Search...', command=start_search)
    btn_apply = tk.Button(frm_settings, text='Apply', command=apply_and_analyze)
    lbl_settings = tk.Label(frm_buttons, text='List of search settings')
    btn_new_settings = tk.Button(frm_buttons, text='Save as new', command=add_search_settings)
    btn_save_settings = tk.Button(frm_buttons, text='Replace selected', command=save_search_settings)
    btn_remove_settings = tk.Button(frm_buttons, text='Remove selected', command=remove_search_settings)
    btn_load_settings = tk.Button(frm_buttons, text='Load from selected', command=retrieve_settings_to_current)

    canvas_image_0 = tk.Canvas(frm_image, width=700, height=700)

    # Listbox creation for all search settings
    search_listbox = tk.Listbox(frm_buttons, height=6, listvariable=search_settings_list)
    insert_search_settings_in_list(search_listbox, search_settings_list)

    btn_open.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    btn_start_search.grid(row=1, column=0, sticky='ew', padx=5)
    frm_settings.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
    frm_canny.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
    lbl_canny_1.grid(row=0, column=0, sticky='ew')
    lbl_canny_2.grid(row=0, column=1, sticky='ew')
    frm_canny_1.grid(row=1, column=0, sticky='ew')
    frm_canny_2.grid(row=1, column=1, sticky='ew')
    frm_colors.grid(row=1, column=0, sticky='ew', padx=5, pady=5)
    frm_search.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
    btn_apply.grid(row=3, column=0, sticky='ew', padx=5, pady=5)
    lbl_settings.grid(row=4, column=0, sticky='ew', padx=5)
    search_listbox.grid(row=5, column=0, sticky='ew', padx=5)
    btn_new_settings.grid(row=6, column=0, sticky='ew', padx=5)
    btn_save_settings.grid(row=7, column=0, sticky='ew', padx=5)
    btn_remove_settings.grid(row=8, column=0, sticky='ew', padx=5)
    btn_load_settings.grid(row=9, column=0, sticky='ew', padx=5)
    frm_buttons.grid(row=0, column=0, sticky='ns')
    frm_image.grid(row=0, column=1, sticky='nsew')

    canvas_image_0.grid(row=0, column=0, sticky='ew', padx=5, pady=5)

    settings_list = [
        Setting(frm_canny_1, 'Gauss blur', search_settings.edges_para.gauss_1, (1, 99), 2, style='buttons'),
        Setting(frm_canny_1, 'Thresh 1', search_settings.edges_para.thresh1_1, (0, 1000), 10, style='buttons'),
        Setting(frm_canny_1, 'Thresh 2', search_settings.edges_para.thresh2_1, (0, 1000), 10, style='buttons'),
        Setting(frm_canny_2, 'Gauss blur', search_settings.edges_para.gauss_2, (1, 99), 2, style='buttons'),
        Setting(frm_canny_2, 'Thresh 1', search_settings.edges_para.thresh1_2, (0, 1000), 10, style='buttons'),
        Setting(frm_canny_2, 'Thresh 2', search_settings.edges_para.thresh2_2, (0, 1000), 10, style='buttons'),
        Setting(frm_colors, 'Use color differences', search_settings.use_color_differences, [], [], style='check_box'),
        Setting(frm_colors, 'R - G', search_settings.color_weights[0], (0, 1), 0.01, style='slider'),
        Setting(frm_colors, 'R - B', search_settings.color_weights[1], (0, 1), 0.01, style='slider'),
        Setting(frm_colors, 'G - B', search_settings.color_weights[2], (0, 1), 0.01, style='slider'),
        Setting(frm_search, 'Max dim of scaled image (pixels)', search_settings.match_para.max_dim, (270, 17280),
                [], style='def'),
        Setting(frm_search, 'Radius to check (pixels)', search_settings.searched_radius, (0, 17280), [], style='def'),
        Setting(frm_search, 'Max number of points', search_settings.contour_para.nb_points, (0, 500), [], style='def'),
        Setting(frm_search, 'Number of search iterations', search_settings.iterations, (0, 20), [], style='def')
    ]

    settings_list[0].set_in_frame(row=0, col=0)
    settings_list[1].set_in_frame(row=1, col=0)
    settings_list[2].set_in_frame(row=2, col=0)
    settings_list[3].set_in_frame(row=0, col=0)
    settings_list[4].set_in_frame(row=1, col=0)
    settings_list[5].set_in_frame(row=2, col=0)
    settings_list[6].set_in_frame(row=0, col=0)
    settings_list[7].set_in_frame(row=1, col=0)
    settings_list[8].set_in_frame(row=2, col=0)
    settings_list[9].set_in_frame(row=3, col=0)
    settings_list[10].set_in_frame(row=0, col=0)
    settings_list[11].set_in_frame(row=1, col=0)
    settings_list[12].set_in_frame(row=2, col=0)
    settings_list[13].set_in_frame(row=3, col=0)

    window.mainloop()

    return image_src_list, search_settings_list


def display(image, i):
    plt.figure(i)
    plt.imshow(image)


def draw_segment(image, point_a, point_b, color, thickness):
    result = image.copy()
    result = cv2.line(result, (point_a.y, point_a.x), (point_b.y, point_b.x), color, thickness)
    return result


def draw_particle_contour(image, particle, color, thickness):
    contour = particle.contour
    result = image.copy()
    n = len(contour)
    if n > 0:
        prev_point = contour[n - 1]
        for i in range(0, n):
            result = draw_segment(result, contour[i], prev_point, color, thickness)
            prev_point = contour[i]

    return result


def display_channel(title, image, channel):
    cv2.imshow(title, image[:, :, channel])


def print_particles(image, particles_list):
    results = image.copy()
    for obj in particles_list:
        results = draw_particle_contour(results, obj, color=(255, 0, 0), thickness=2)

    return results
