try:
    import Cui
    application="Studio"
except:
    try:
        import MatadorScript
        application="Matador"
    except:
        application="Standalone"
