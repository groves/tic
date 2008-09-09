package sevorg.tic.model

import javax.persistence.{EntityManager,EntityTransaction,Persistence}

import scala.collection.jcl.{BufferWrapper,SetWrapper}

object Model {
  val emVar = new ThreadLocal[EntityManager];
  def em = emVar.get();

  def intx(f: Unit) = withtx((tx: EntityTransaction) => {f})

  def withtx(f: (EntityTransaction) => Unit) = {
    val tx = em.getTransaction()
    try { 
      tx.begin()
      f(tx)
      tx.commit()
    } catch {
      case _ => tx.rollback()
    }
  }

  implicit def setToWrapper[A](set : java.util.Set[A]) = new SetWrapper[A]{override def underlying = set}
  implicit def listToWrapper[A](list : java.util.List[A]) = new BufferWrapper[A]{override def underlying = list}
}

