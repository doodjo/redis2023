import redis


#Da bi se implementirala funkcionalnost lajkovanja lokacije potreban je python file koji ce da kreira kljuceve i vrednosti unutar niza dictionary-ja
#Na ovaj nacin mozemo da manipulisemo podacima koji se javljaju unutar db-ja kao sto je broj lajkova lokacije na primer

r = redis.Redis('192.168.99.100')

grad = [
    {
        "Grad": "Melburn",
        "Drzava": "Viktorija",
        "nLikes": 0,

    },

    {
        "Grad": "Kanbera",
        "Drzava": "Novi Južni Vels",
        "nLikes": 0,
    },

    {
        "Grad": "Pert",
        "Drzava": "Zapadna Australija",
        "nLikes": 0,
    },

    {
        "Grad": "Sidnej",
        "Drzava": "Novi Južni Vels",
        "nLikes": 0,
    }

]

gradovi = dict()
id = 1
for i in grad:
    key = f"Grad Numero: {id}"
    gradovi[key] = i
    id += 1

print(gradovi)


pipe = r.pipeline() #Koriscenje piepline-a, zato sto se baza pogadja za svaku iteraciju for petlje, preko pipeline-a gadja se samo pipeline (jednom)
                    #Ako for ima 10 000 iteracija, gadjace se baza 10 000 puta. Problem!
for grad_id, grad in gradovi.items():
    for field, value in grad.items():
        pipe.hset(grad_id, field, value)

pipe.execute() #Pokretanje pipeline-a

r.close()