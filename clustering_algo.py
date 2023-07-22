import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

def check_integer(string):

    try:

        val = int(string)
        return True
    
    except ValueError:
        return False

def gmm_algo(cur_order, actual_data, val_cache):

    total_orders = cur_order

    products = []

    each_item_prodcut = []

    for each_input in actual_data:

        each_item_prodcut.append(each_input[1])

    total = sum(each_item_prodcut) + len(each_item_prodcut)


    first = []

    second = []

    for each_order in total_orders:

        if each_order["val"] not in val_cache.store:

            if "substring" not in each_order["val"]:
                
                first.append(each_order)

            else:

                second.append(each_order)

    count = 0

    assign = True

    for each in first:

        products.append(each)

        count += len(each["val"])

        if count > total:

            assign = False

            break

    if assign:

        for each in second:

            products.append(each)

            count += len(each["val"])

            if count > total:

                break

    matrix = []

    total_wraps = 10000

    for each_order in products:

        row = [0 for product in range(total_wraps)]

        for each_item in each_order["val"]:

            if len(each_item["val"])>0:

                if each_item["val"][0] == "X":

                    if check_integer(each_item["val"][1:]):

                        row[int(each_item["val"][1:])-1] = 1


                elif each_item["val"][0] == "Y":

                    if check_integer(each_item["val"][1:]):

                        if int(each_item["val"][1:]) <= 1500:

                            row[1601+int(each_item["val"][1:])-1] = 1

                        else:

                            row[1601+int(each_item["val"][1:])-1-3499] = 1

                elif each_item["val"][0] == "Z":

                    if check_integer(each_item["val"][1:]):

                        row[4101+int(each_item["val"][1:])-1] = 1

        matrix.append(row)

    matrix = np.array(matrix)


    number_of_iterations = 20
    number_of_k = len(each_item_prodcut)


    numerical_data = matrix.astype(float)

    n_components = 20  
    pca = PCA(n_components=n_components)
    reduced_features = pca.fit_transform(numerical_data)


    def gmm(kmeans_toggle):

        cache = {}

        max_val = float("-inf")

        num_runs = 10

        best_kmeans = None
        best_inertia = float('inf')

        if kmeans_toggle:

            for _ in range(num_runs):
                kmeans = KMeans(n_clusters=number_of_k)
                kmeans.fit(reduced_features)
                if kmeans.inertia_ < best_inertia:
                    best_kmeans = kmeans
                    best_inertia = kmeans.inertia_

            cluster_means = best_kmeans.cluster_centers_

        for i in range(number_of_iterations):

            if kmeans_toggle:

                gmm = GaussianMixture(n_components=number_of_k, means_init=cluster_means)

            else:
                gmm = GaussianMixture(n_components=number_of_k)

            gmm.fit(reduced_features)
            cluster_assignments = gmm.predict(reduced_features)

            if tuple(cluster_assignments) not in cache.keys():

                cache[tuple(cluster_assignments)] = 0

            else:

                cache[tuple(cluster_assignments)]+= 1

        for key,value in cache.items():

            if value > max_val:

                final_assignment = key

                max_val = value

        clusters = [[] for _ in range(number_of_k)]

        for order_index, cluster_index in enumerate(final_assignment):
            clusters[cluster_index].append(order_index)


        return clusters


    def processing_function(clusters):

        assigned_products = {}

        index = 1

        for cluster in clusters:

            assigned_products[index] = []

            each_assigned_order = []

            for each_cluster in cluster:

                prod = products[each_cluster]

                each_assigned_order.append([len(prod["val"]),products[each_cluster]])

            assigned_products[index].append(each_assigned_order)

            index+=1

        
        tmp_output = []

        for key,value in assigned_products.items():

            tmp_output.append(value)
            

        cluster_products = tmp_output

        cluster_products.sort(key=lambda x: len(x[0]), reverse=True)

        cluster_products = sorted(cluster_products, key=len, reverse=True)

        cluster_member = [row[:] for row in actual_data]

        cluster_member.sort(key=lambda x: x[1], reverse=True)


        product_total = []

        for i in cluster_products:
            tmp = 0

            for j in i[0]:

                tmp+=j[0]

            product_total.append(tmp)


        final_clsut = {}

        for i in cluster_member:

            final_clsut[i[0]] = []


        index = [0 for i in range(len(cluster_products))]


        for i in range(len(cluster_products)):

            cur = cluster_products[i][0]

            for each in range(len(cur)):

                index[i] = each

                if len(cur)-1 == index[i]:

                    index[i] = None

                val_prod = product_total[i] - cur[each][0]

                val_person = cluster_member[i][1] - cur[each][0]

                final_clsut[cluster_member[i][0]].append(cur[each][1])

                if val_prod <= 0:

                    product_total[i] = 0

                    cluster_member[i][1] = max(val_person,0)

                    break

                elif val_person <= 0:

                    cluster_member[i][1] = 0

                    product_total[i] = max(val_prod,0)

                    break

                product_total[i] = val_prod

                cluster_member[i][1] = val_person


        for i in range(len(cluster_member)):

            while cluster_member[i][1] > 0:

                if not any(index):

                    break

                for j in range(len(index)):

                    if index[j] != None and index[j] != 0:

                        if len(cluster_products[j][0]) == index[j]:

                            index[j] = None

                            continue
                        
                        final_clsut[cluster_member[i][0]].append(cluster_products[j][0][index[j]][1])

                        cluster_member[i][1] = cluster_member[i][1] - cluster_products[j][0][index[j]][0]

                        index[j]+=1

                        if cluster_member[i][1] < 0:

                            cluster_member[i][1] = 0


        ans = 0

        for key,val in final_clsut.items():

            final_count = set()

            for each_set in val:

                    for f in each_set["val"]:

                        final_count.add(f["val"])

            ans+= len(final_count)

        return (ans/len(cluster_products),final_clsut)

    mean_min = float('inf')

    for i in range(10):

        clusters = gmm(True)

        val,mapping = processing_function(clusters)

        if val < mean_min:

            final_mapping = mapping

            mean_min = val

    for i in range(10):

        clusters = gmm(False)

        val,mapping = processing_function(clusters)

        if val < mean_min:

            final_mapping = mapping

            mean_min = val
          
    output = {}

    for key,value in final_mapping.items():

        tmp_list = []

        for each_val in value:

            tmp_list.append(each_val["val"])

        output[key] = tmp_list


    return output
