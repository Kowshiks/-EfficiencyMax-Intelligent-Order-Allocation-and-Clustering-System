import requests
import numpy as np
from sklearn.mixture import GaussianMixture
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import warnings
import app_main

warnings.filterwarnings("ignore", category=FutureWarning)


def is_integer(string):
    try:
        int_value = int(string)
        return True
    except ValueError:
        return False

def algo(cur_order, actual_data, val_cache):

    all_orders = cur_order
    orders = []


    wraps_per_person = []

    for each_input in actual_data:

        wraps_per_person.append(each_input[1])

    total = sum(wraps_per_person) + 5*len(wraps_per_person)



    priority_shipping = []

    normal_shipping = []

    for each_order in all_orders:

        if each_order["val"] not in val_cache.store:

            if "Free" not in each_order["val"]:
                
                priority_shipping.append(each_order)



            else:

                normal_shipping.append(each_order)

    count = 0

    assign = True

    for each in priority_shipping:

        orders.append(each)

        count += len(each["val"])

        if count > total:

            assign = False

            break

    if assign:

        for each in normal_shipping:

            orders.append(each)

            count += len(each["val"])

            if count > total:

                break

    matrix = []

    total_wraps = 8100

    for each_order in orders:

        row = [0 for product in range(total_wraps)]

        for each_item in each_order["items"]:

            if len(each_item["val"])>0:

                if each_item["val"][0] == "A":

                    if is_integer(each_item["val"][1:]):

                        row[int(each_item["val"][1:])-1] = 1


                elif each_item["val"][0] == "P":

                    if is_integer(each_item["val"][1:]):

                        if int(each_item["val"][1:]) <= 1500:

                            row[1601+int(each_item["val"][1:])-1] = 1

                        else:

                            row[1601+int(each_item["val"][1:])-1-3499] = 1

                elif each_item["val"][0] == "T":

                    if is_integer(each_item["val"][1:]):

                        row[4101+int(each_item["val"][1:])-1] = 1

        matrix.append(row)

    matrix = np.array(matrix)




    number_of_iterations = 20
    number_of_shipstation = len(wraps_per_person)





    ##################  Function to perform GMM  ############################



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
                kmeans = KMeans(n_clusters=number_of_shipstation)
                kmeans.fit(reduced_features)
                if kmeans.inertia_ < best_inertia:
                    best_kmeans = kmeans
                    best_inertia = kmeans.inertia_

            cluster_means = best_kmeans.cluster_centers_

        for i in range(number_of_iterations):

            if kmeans_toggle:

                gmm = GaussianMixture(n_components=number_of_shipstation, means_init=cluster_means)

            else:
                gmm = GaussianMixture(n_components=number_of_shipstation)

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

        clusters = [[] for _ in range(number_of_shipstation)]

        for order_index, cluster_index in enumerate(final_assignment):
            clusters[cluster_index].append(order_index)


        return clusters


    ##############################################################################################################



    def code(clusters):



        assigned_orders = {}

        index = 1


        for cluster in clusters:

            assigned_orders[index] = []

            each_assigned_order = []

            for each_cluster in cluster:

                prod = orders[each_cluster]

                each_assigned_order.append([len(prod["items"]),orders[each_cluster]])

            assigned_orders[index].append(each_assigned_order)

            index+=1

        







        output_cl = []

        for key,value in assigned_orders.items():

            output_cl.append(value)
            

        order_cluster = output_cl


        order_cluster.sort(key=lambda x: len(x[0]), reverse=True)

        order_cluster = sorted(order_cluster, key=len, reverse=True)

        people_work = [row[:] for row in actual_data]

        people_work.sort(key=lambda x: x[1], reverse=True)


        order_sum = []

        for i in order_cluster:
            tmp = 0

            for j in i[0]:

                tmp+=j[0]

            order_sum.append(tmp)








        ####################################  Assign people with all orders in the initial cluster ###############################



        final_seg = {}

        for i in people_work:

            final_seg[i[0]] = []


        index = [0 for i in range(len(order_cluster))]


        for i in range(len(order_cluster)):

            cur = order_cluster[i][0]

            for each in range(len(cur)):

                index[i] = each

                if len(cur)-1 == index[i]:

                    index[i] = None

                val_prod = order_sum[i] - cur[each][0]

                val_person = people_work[i][1] - cur[each][0]

                final_seg[people_work[i][0]].append(cur[each][1])

                if val_prod <= 0:

                    order_sum[i] = 0

                    people_work[i][1] = max(val_person,0)

                    break

                elif val_person <= 0:

                    people_work[i][1] = 0

                    order_sum[i] = max(val_prod,0)

                    break

                order_sum[i] = val_prod

                people_work[i][1] = val_person



        ####################################################################################################################






        ######################## If the workers still have orders left then assign by checking other clusters #########################


        for i in range(len(people_work)):

            while people_work[i][1] > 0:

                if not any(index):

                    break

                for j in range(len(index)):

                    if index[j] != None and index[j] != 0:

                        if len(order_cluster[j][0]) == index[j]:

                            index[j] = None

                            continue
                        
                        final_seg[people_work[i][0]].append(order_cluster[j][0][index[j]][1])

                        people_work[i][1] = people_work[i][1] - order_cluster[j][0][index[j]][0]

                        index[j]+=1

                        if people_work[i][1] < 0:

                            people_work[i][1] = 0


        #################################################################################################################

        ans = 0

        for key,val in final_seg.items():

            final_count = set()

            for each_set in val:

                    for f in each_set["items"]:

                        final_count.add(f["val"])

            ans+= len(final_count)

        return (ans/len(order_cluster),final_seg)



    #################################################################################################################



    mean_min = float('inf')

    for i in range(10):

        clusters = gmm(True)

        val,mapping = code(clusters)

        if val < mean_min:

            final_mapping = mapping

            mean_min = val



    for i in range(10):

        clusters = gmm(False)

        val,mapping = code(clusters)

        if val < mean_min:

            final_mapping = mapping

            mean_min = val


    output = {}

    for key,value in final_mapping.items():

        tmp_list = []

        for each_val in value:

            tmp_list.append(each_val["orderId"])

        output[key] = tmp_list


    return output

   

