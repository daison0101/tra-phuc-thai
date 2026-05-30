from app import app, db, Product

with app.app_context():

    tea1 = Product(
        name='Trà Hoa Cúc',
        price=50000,
        description='Giúp ngủ ngon',
        image='https://images.unsplash.com/photo-1576092768241-dec231879fc3?q=80&w=800'
    )

    tea2 = Product(
        name='Trà Matcha',
        price=80000,
        description='Tăng năng lượng',
        image='https://images.unsplash.com/photo-1558160074-4d7d8bdf4256?q=80&w=800'
    )

    tea3 = Product(
        name='Trà Ô Long',
        price=120000,
        description='Hỗ trợ giảm cân',
        image='https://images.unsplash.com/photo-1515823064-d6e0c04616a7?q=80&w=800'
    )

    db.session.add_all([
        tea1,
        tea2,
        tea3
    ])

    db.session.commit()

    print("Data inserted!")